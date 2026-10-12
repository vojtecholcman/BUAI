# Jezdec na 4x4 šachovnici
pohyby = [(2,1), (1,2), (-1,2), (-2,1), (-2,-1), (-1,-2), (1,-2), (2,-1)]

def sousedi(x, y):
    for dx, dy in pohyby:
        nx, ny = x+dx, y+dy
        if 0 <= nx < 4 and 0 <= ny < 4:
            yield (nx, ny)

start = (0,0)  # A1
cíl = (3,3)    # D4

from collections import deque
fronta = deque([(start, [start])])
navštíveno = set([start])

while fronta:
    (x,y), cesta = fronta.popleft()
    if (x,y) == cíl:
        print("Cesta nalezena:", cesta)
        break
    for s in sousedi(x,y):
        if s not in navštíveno:
            navštíveno.add(s)
            fronta.append((s, cesta+[s]))

