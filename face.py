import cv2
import random
import numpy as np
from ultralytics import YOLO

# 1. โหลดโมเดล (ใช้ตัวที่เร็วที่สุดของคุณ)
model = YOLO('face.pt') 

# 2. ตั้งค่ากล้อง
cap = cv2.VideoCapture(0)
cap.set(3, 640) # กว้าง
cap.set(4, 480) # สูง

# --- ตัวแปรสำหรับเกม ---
game_over = False
score = 0
obstacles = []  # เก็บรายการสิ่งกีดขวาง [x, y, speed]
player_box = None # เก็บตำแหน่งหน้าเรา

print("🎮 เริ่มเกม! ขยับหน้าเพื่อหลบลูกบอลสีแดง... (กด 'r' เพื่อเริ่มใหม่, 'q' ออก)")

while cap.isOpened():
    success, frame = cap.read()
    if not success:
        break

    # กลับด้านภาพ (Mirror) เพื่อให้ควบคุมง่ายเหมือนส่องกระจก
    frame = cv2.flip(frame, 1)
    height, width, _ = frame.shape

    # --- ส่วนของ AI (YOLO) ---
    if not game_over:
        # ใช้ imgsz=320 เพื่อความลื่นไหลสูงสุดของเกม
        results = model.predict(source=frame, stream=True, conf=0.5, imgsz=320, verbose=False)
        
        player_detected = False
        for r in results:
            boxes = r.boxes
            if len(boxes) > 0:
                # เอาเฉพาะใบหน้าแรกที่เจอ (คนที่ใหญ่ที่สุด)
                box = boxes[0]
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                player_box = (x1, y1, x2, y2)
                player_detected = True
                
                # วาดกรอบสีเขียวรอบหน้า (ตัวละครเรา)
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.putText(frame, "PLAYER", (x1, y1-10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

        # --- ส่วนของระบบเกม ---
        if player_detected:
            score += 1 # คะแนนเพิ่มตามเวลาที่รอด

            # 1. สร้างสิ่งกีดขวางใหม่ (สุ่มโอกาส 10% ต่อเฟรม)
            if random.randint(0, 100) < 10: 
                obj_x = random.randint(20, width - 20)
                obj_y = 0
                obj_speed = random.randint(5, 10) # สุ่มความเร็ว
                obstacles.append([obj_x, obj_y, obj_speed])

            # 2. อัปเดตตำแหน่งสิ่งกีดขวาง
            for obj in obstacles:
                obj[1] += obj[2] # ขยับลงตามแกน Y

                # วาดวงกลมสีแดง (ระเบิด)
                cv2.circle(frame, (obj[0], obj[1]), 15, (0, 0, 255), -1)

                # 3. เช็คการชน (Collision Detection)
                # ถ้าระเบิด (จุดกึ่งกลาง) เข้ามาอยู่ในกรอบหน้าเรา
                px1, py1, px2, py2 = player_box
                if px1 < obj[0] < px2 and py1 < obj[1] < py2:
                    game_over = True
                    print(f"💥 ชนแล้ว! คะแนนรวม: {score}")

            # ลบสิ่งกีดขวางที่ตกเลยขอบจอไปแล้ว (เพื่อไม่ให้กินแรม)
            obstacles = [obj for obj in obstacles if obj[1] < height]

    # --- แสดงผลหน้าจอ Game Over ---
    else:
        # วาดหน้าจอสีดำจางๆ
        overlay = frame.copy()
        cv2.rectangle(overlay, (0, 0), (width, height), (0, 0, 0), -1)
        cv2.addWeighted(overlay, 0.7, frame, 0.3, 0, frame)
        
        # ข้อความจบเกม
        cv2.putText(frame, "GAME OVER", (width//2 - 150, height//2 - 50), 
                    cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 255), 4)
        cv2.putText(frame, f"Score: {score}", (width//2 - 80, height//2 + 20), 
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        cv2.putText(frame, "Press 'r' to Restart", (width//2 - 120, height//2 + 70), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (200, 200, 200), 1)

    # แสดงคะแนนมุมจอ
    cv2.putText(frame, f"Score: {score}", (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2)

    cv2.imshow("Face Dodge Game - YOLO", frame)

    # ปุ่มควบคุม
    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'): # ออกเกม
        break
    elif key == ord('r') and game_over: # เริ่มใหม่
        game_over = False
        score = 0
        obstacles = []

cap.release()
cv2.destroyAllWindows()
