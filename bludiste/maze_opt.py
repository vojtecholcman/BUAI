"""Paměťově optimalizované řešení (volitelná část, +5 b).

Hlavní myšlenka: celý stav BFS se vejde do 2 BITŮ NA POLE.

Každé pole má jeden ze 4 stavů (2 bity):
    0 = FREE    volné, zatím nenavštívené
    1 = WALL    překážka
    2 = VIS0    navštívené, bit b = 0
    3 = VIS1    navštívené, bit b = 1
kde b = (d // 2) % 2 a d je vzdálenost pole od startu.

Proč stačí jediný bit b místo celé vzdálenosti nebo ukazatele na rodiče:
  * Mřížka je bipartitní graf (šachovnice): sousedé mají vždy různou
    paritu x+y, takže vzdálenosti sousedů se liší PŘESNĚ o 1 (nikdy o 0).
  * Při zpětném průchodu z pole se vzdáleností d proto mají navštívení
    sousedé vzdálenost buď d-1 (krok zpět ke startu), nebo d+1.
  * d-1 a d+1 se liší o 2, takže (d-1)//2 a (d+1)//2 se liší o 1
    a mají RŮZNÝ bit b. Podle b tedy poznáme, kterým směrem je start.

Další úspory:
  * generátor nepotřebuje seznam všech indexů (random.sample by vytvořil
    pomocný seznam n² prvků); překážky se losují přímo do mřížky,
  * BFS běží po vrstvách se dvěma kompaktními poli array('I'), 4 B na prvek,
    a drží jen aktuální a následující vrstvu,
  * výsledná cesta se ukládá jako posloupnost směrů (1 B na krok).
"""
import math
import random
from array import array

FREE, WALL, VIS0, VIS1 = 0, 1, 2, 3

# směry kroku (z předchozího pole na další)
UP, DOWN, LEFT, RIGHT = 0, 1, 2, 3
ARROWS = "^v<>"


# ---------- práce s 2bitovou mřížkou ----------

def new_grid(n):
    """Mřížka n×n, vše FREE. 4 pole na bajt."""
    return bytearray((n * n + 3) // 4)


def get(g, i):
    return (g[i >> 2] >> ((i & 3) << 1)) & 3


def mark(g, i, v):
    """Nastaví stav pole, které je aktuálně FREE (0) – stačí OR."""
    g[i >> 2] |= v << ((i & 3) << 1)


# ---------- generátor ----------

def generate_maze(n, ratio=0.4, seed=None):
    """Náhodně rozmístí ceil(ratio * n²) překážek; start i cíl zůstanou volné.
    Losování s odmítnutím: náhodné pole, a pokud už je zeď, losuje se znovu.
    Při 40 % zaplnění je potřeba v průměru ~1,28 pokusu na překážku
    a nevzniká žádná pomocná struktura o velikosti n²."""
    if n < 2:
        raise ValueError("n musí být alespoň 2")
    N = n * n
    k = math.ceil(ratio * N)
    if k > N - 2:
        raise ValueError(f"{k} překážek se nevejde do {N - 2} volných polí")
    rng = random.Random(seed)
    g = new_grid(n)
    placed = 0
    rr = rng.randrange
    while placed < k:
        i = rr(1, N - 1)          # nikdy start (0) ani cíl (N-1)
        if get(g, i) == FREE:
            mark(g, i, WALL)
            placed += 1
    return g


def from_bytes(grid1, n):
    """Převod mřížky z maze.py (1 bajt na pole) do 2bitové – kvůli testům."""
    g = new_grid(n)
    for i in range(n * n):
        if grid1[i]:
            mark(g, i, WALL)
    return g


# ---------- BFS ----------

def bfs(g, n):
    """BFS po vrstvách přímo v 2bitové mřížce (mřížku přepisuje!).
    Vrátí (délka, moves), kde moves je bytearray směrů UP/DOWN/LEFT/RIGHT
    od startu k cíli, nebo None, pokud cesta neexistuje."""
    N = n * n
    goal = N - 1
    typecode = "I" if N < 2**32 else "Q"

    mark(g, 0, VIS0)              # start: d = 0 -> b = 0
    if goal == 0:
        return 0, bytearray()

    cur = array(typecode, [0])
    d = 0
    last_row = N - n
    while cur:
        d += 1
        lab = VIS1 if (d >> 1) & 1 else VIS0
        nxt = array(typecode)
        push = nxt.append
        for i in cur:
            x = i % n
            # 4 sousedé; podmínky hlídají okraje mřížky
            if i >= n:
                j = i - n
                if (g[j >> 2] >> ((j & 3) << 1)) & 3 == FREE:
                    g[j >> 2] |= lab << ((j & 3) << 1)
                    push(j)
            if i < last_row:
                j = i + n
                if (g[j >> 2] >> ((j & 3) << 1)) & 3 == FREE:
                    g[j >> 2] |= lab << ((j & 3) << 1)
                    if j == goal:
                        return d, reconstruct(g, n, d)
                    push(j)
            if x > 0:
                j = i - 1
                if (g[j >> 2] >> ((j & 3) << 1)) & 3 == FREE:
                    g[j >> 2] |= lab << ((j & 3) << 1)
                    push(j)
            if x < n - 1:
                j = i + 1
                if (g[j >> 2] >> ((j & 3) << 1)) & 3 == FREE:
                    g[j >> 2] |= lab << ((j & 3) << 1)
                    if j == goal:
                        return d, reconstruct(g, n, d)
                    push(j)
        cur = nxt                 # předchozí vrstva se uvolní
    return None


def reconstruct(g, n, D):
    """Zpětný průchod z cíle: z pole se vzdáleností t jdeme na souseda
    se vzdáleností t-1, poznaného podle bitu b = ((t-1)//2) % 2."""
    N = n * n
    i = N - 1
    moves = bytearray(D)
    for t in range(D, 0, -1):
        want = VIS1 if ((t - 1) >> 1) & 1 else VIS0
        x = i % n
        # soused nad námi => do i jsme přišli krokem DOLŮ, atd.
        if i >= n and get(g, i - n) == want:
            i -= n; moves[t - 1] = DOWN
        elif i < N - n and get(g, i + n) == want:
            i += n; moves[t - 1] = UP
        elif x > 0 and get(g, i - 1) == want:
            i -= 1; moves[t - 1] = RIGHT
        elif x < n - 1 and get(g, i + 1) == want:
            i += 1; moves[t - 1] = LEFT
        else:
            raise AssertionError("rekonstrukce selhala – nemělo by nastat")
    assert i == 0
    return moves


def path_cells(n, moves):
    """Převede směry na indexy polí (generátor, nic neukládá)."""
    i = 0
    yield i
    step = (-n, n, -1, 1)
    for m in moves:
        i += step[m]
        yield i


def print_maze(g, n, moves=None):
    on_path = set(path_cells(n, moves)) if moves is not None else set()
    for y in range(n):
        row = []
        for x in range(n):
            i = y * n + x
            if i == 0:
                row.append("S")
            elif i == n * n - 1:
                row.append("G")
            elif get(g, i) == WALL:
                row.append("#")
            elif i in on_path:
                row.append("*")
            else:
                row.append(".")
        print(" ".join(row))


if __name__ == "__main__":
    import sys
    import time
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 100
    seed = int(sys.argv[2]) if len(sys.argv) > 2 else None

    t0 = time.perf_counter()
    g = generate_maze(n, seed=seed)
    t1 = time.perf_counter()
    res = bfs(g, n)
    t2 = time.perf_counter()

    print(f"n={n}, seed={seed}, mřížka: {len(g):,} B")
    print(f"generování {t1 - t0:.2f} s, BFS {t2 - t1:.2f} s")
    if res is None:
        print("cesta NEEXISTUJE")
    else:
        D, moves = res
        print(f"nejkratší cesta: {D} kroků")
        if n <= 30:
            print_maze(g, n, moves)
