user_input = input()
i = list(map(float, user_input.split()))

if i.index(max(i)) > i.index(min(i)):
	for _ in range(len(i)):
		if i[0] > min(i):
			i.remove(i[0])
else:
	r = len(i) - (i.index(max(i)) + 1)
	for _ in range(r):
		i.remove(len(i) - 1)

print(f"{r}")
