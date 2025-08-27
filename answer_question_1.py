user_input = input()
i = list(map(float, user_input.split()))

i.remove(min(i))
i.remove(max(i))

a = sum(i) / len(i)

print(f"{a:.2f}")
