user_input = input()
i = list(map(float, user_input.split()))
j = list(map(float, i))

if i.index(min(i)) < i.index(max(i)):
    for _ in range(len(i)):
        if i[0] > min(i):
            i.remove(i[0])
    a = max(i) - min(i)
    print(f"a1 = {a}")
   
else:
    r = len(i) - (i.index(max(i)) + 1)
    for _ in range(r):
        i.pop()
    if (max(i) - min(i)) < (max(j) - min(j)) and i.index(min(i)) < i.index(max(i)):
        c = max(j) - min(j)
        print(f"c1 = {c}")            
    else:
        
        a = max(i) - min(i)
        print(f"a2 = {a}")
