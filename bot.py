# bot.py
"""
Entry point ของบอท:
- ฟัง incoming events (challenges, gameStart)
- สำหรับแต่ละเกม จะ spawn handler (thread) ที่ stream สถานะเกม (ถ้าได้) หรือ poll เป็น fallback
- ตัดสินใจเดินโดยเรียก engine.get_best_move()
"""

import threading
import time
import traceback
import berserk
import berserk.exceptions
from config import TOKEN, POLL_INTERVAL
from engine import Engine

# สร้าง session และ client
session = berserk.TokenSession(TOKEN)
client = berserk.Client(session=session)


def _parse_moves_from_state(state):
    """
    รองรับหลายรูปแบบของ state ที่อาจได้จาก stream หรือ export
    คืน string ของ moves (space-separated UCI) หรือ "" ถ้าไม่มี
    """
    if not state:
        return ""
    # state อาจเป็น dict หรือ string
    if isinstance(state, dict):
        # direct moves
        if "moves" in state:
            return state.get("moves", "") or ""
        # nested under 'state'
        if "state" in state and isinstance(state["state"], dict):
            return state["state"].get("moves", "") or ""
        # sometimes gameFull structure
        if state.get("type") == "gameFull" and isinstance(state.get("state"), dict):
            return state["state"].get("moves", "") or ""
        # fallback: maybe 'state' already given
        return ""
    if isinstance(state, str):
        return state
    return ""


def handle_game(game_id: str, my_color: str):
    """
    จัดการเกมเดียว: stream สถานะหรือ poll แล้วตอบ move เมื่อเป็นตาของบอท
    my_color: "white" หรือ "black"
    """
    print(f"[handler] start game handler {game_id} (color={my_color})")
    last_processed_moves_count = -1

    # Try using streaming game state (preferred)
    try:
        stream = client.bots.stream_game_state(game_id)
    except Exception:
        stream = None

    if stream:
        # ใช้ stream ถ้าใช้งานได้
        try:
            for state in stream:
                try:
                    # state อาจเป็น dict แบบหลายชั้น
                    moves_str = _parse_moves_from_state(state)
                    moves_list = moves_str.split() if moves_str else []
                    moves_count = len(moves_list)

                    # check game status if available
                    status = None
                    if isinstance(state, dict):
                        # state['state'] อาจมี 'status'
                        if "state" in state and isinstance(state["state"], dict):
                            status = state["state"].get("status")
                        else:
                            status = state.get("status")

                    if status and status != "started":
                        print(f"[handler:{game_id}] เกมจบ (status={status})")
                        break

                    # determine who to move: even -> white, odd -> black
                    to_move_color = "white" if (moves_count % 2 == 0) else "black"

                    # ถ้าเป็นตาของบอท และยังไม่เคย process สถานะนี้
                    if to_move_color == my_color and last_processed_moves_count != moves_count:
                        move = get_best_move(state)
                        if move:
                            try:
                                client.bots.make_move(game_id, move)
                                print(f"[handler:{game_id}] ส่ง move {move} (moves_count={moves_count})")
                                # mark processed for current moves_count
                                last_processed_moves_count = moves_count
                            except berserk.exceptions.ResponseError as err:
                                # อาจเกิด Not your turn (race) — log แล้วรอ
                                print(f"[handler:{game_id}] ไม่สามารถส่ง move: {err}")
                        else:
                            print(f"[handler:{game_id}] engine คืน None (no move).")
                    # else: ถ้าไม่ใช่ตา หรือตำแหน่งนี้ process แล้ว ให้รอต่อ
                except Exception:
                    print(f"[handler:{game_id}] error processing state:\n{traceback.format_exc()}")
                    time.sleep(POLL_INTERVAL)
        except Exception:
            # stream อาจถูกตัด — fallback ไป polling
            print(f"[handler:{game_id}] stream ตัด, fallback เป็น polling")
            # fallthrough to polling section below
    # Fallback: polling using client.games.export
    try:
        while True:
            try:
                game_state = client.games.export(game_id)
            except berserk.exceptions.ResponseError as e:
                print(f"[handler:{game_id}] ไม่สามารถดึงสถานะเกม (export): {e}")
                break

            status = game_state.get("status")
            if status and status != "started":
                print(f"[handler:{game_id}] เกมจบ (status={status})")
                break

            moves_str = game_state.get("moves", "") or ""
            moves_list = moves_str.split() if moves_str else []
            moves_count = len(moves_list)

            to_move_color = "white" if (moves_count % 2 == 0) else "black"

            if to_move_color == my_color and last_processed_moves_count != moves_count:
                move = get_best_move(game_state)
                if move:
                    try:
                        client.bots.make_move(game_id, move)
                        print(f"[handler:{game_id}] (poll) ส่ง move {move} (moves_count={moves_count})")
                        last_processed_moves_count = moves_count
                    except berserk.exceptions.ResponseError as err:
                        print(f"[handler:{game_id}] (poll) ไม่สามารถส่ง move: {err}")
                else:
                    print(f"[handler:{game_id}] (poll) engine คืน None")
            time.sleep(POLL_INTERVAL)
    except Exception:
        print(f"[handler:{game_id}] handler exception:\n{traceback.format_exc()}")

    print(f"[handler] end game handler {game_id}")


def main():
    print("Bot เริ่มทำงาน... รอ challenge...")
    for event in client.bots.stream_incoming_events():
        try:
            etype = event.get("type")
            if etype == "challenge":
                challenge_id = event["challenge"]["id"]
                print(f"มี challenge ใหม่: {challenge_id}, ตอบรับ...")
                try:
                    client.bots.accept_challenge(challenge_id)
                except berserk.exceptions.ResponseError as e:
                    print(f"ไม่สามารถตอบรับ challenge: {e}")
                continue

            if etype == "gameStart":
                game_id = event["game"]["id"]
                my_color = event["game"].get("color")  # "white" or "black"
                # spawn handler thread per game (daemon เพื่อให้ main thread ไม่บล็อก)
                t = threading.Thread(target=handle_game, args=(game_id, my_color), daemon=True)
                t.start()
        except Exception:
            print(f"error in main event loop:\n{traceback.format_exc()}")


if __name__ == "__main__":
    main()
