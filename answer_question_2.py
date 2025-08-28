user_input = input()
i = list(map(float, user_input.split()))

if i.index(min(i)) < i.index(max(i)):
	for _ in range(len(i)):
		if i[0] > min(i):
			i.remove(i[0])
else:
	r = len(i) - (i.index(max(i)) + 1)
	for _ in range(r):
		i.pop()

a = max(i) - min(i)
print(f"{a}")
