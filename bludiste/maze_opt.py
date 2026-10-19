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
    a nevzniká žádná pomocná struktura o velikosti n².
    Pro ratio > 50 % se postupuje obráceně (všude zeď a losují se volná
    pole), aby losování nezpomalovalo při téměř plné mřížce."""
    if n < 2:
        raise ValueError("n musí být alespoň 2")
    if not 0 <= ratio <= 1:
        raise ValueError("podíl překážek musí být mezi 0 a 1")
    N = n * n
    k = math.ceil(ratio * N)
    if k > N - 2:
        raise ValueError(f"{k} překážek se nevejde do {N - 2} volných polí")
    rng = random.Random(seed)
    rr = rng.randrange
    if k <= (N - 2) // 2:
        g = new_grid(n)
        placed = 0
        while placed < k:
            i = rr(1, N - 1)      # nikdy start (0) ani cíl (N-1)
            if get(g, i) == FREE:
                mark(g, i, WALL)
                placed += 1
    else:
        g = bytearray(b"\x55" * ((N + 3) // 4))   # 01010101 = 4× WALL
        clear(g, 0)
        clear(g, N - 1)
        freed, to_free = 0, N - 2 - k
        while freed < to_free:
            i = rr(1, N - 1)
            if get(g, i) == WALL:
                clear(g, i)
                freed += 1
    return g


def clear(g, i):
    """Nastaví pole na FREE."""
    g[i >> 2] &= ~(3 << ((i & 3) << 1)) & 0xFF


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


def peak_memory_mb():
    """Špičková paměť procesu v MB (Linux/macOS); na Windows None."""
    try:
        import resource
    except ImportError:
        return None
    import sys
    r = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    return r / 1024 / 1024 if sys.platform == "darwin" else r / 1024


DEFAULT_PERCENT = 40      # zadání: alespoň 40 % překážek


def read_input():
    """Hrana n, seed a procento překážek z příkazové řádky:
        python3 maze_opt.py n [seed] [procento]     (seed "-" = náhodný)
    bez argumentů se program zeptá. Seed i procento jsou nepovinné.
    Když seed chybí, vylosuje se a vypíše, aby šlo bludiště zopakovat."""
    import sys
    args = sys.argv[1:]
    if args:
        n = int(args[0])
        seed = int(args[1]) if len(args) > 1 and args[1] != "-" else None
        percent = float(args[2]) if len(args) > 2 else DEFAULT_PERCENT
    else:
        n = int(input("Zadej velikost hrany bludiště n: "))
        s = input(f"Procento překážek (Enter = {DEFAULT_PERCENT}): ").strip()
        percent = float(s.replace(",", ".")) if s else DEFAULT_PERCENT
        s = input("Seed (Enter = náhodné bludiště): ").strip()
        seed = int(s) if s else None
    if n < 2:
        raise SystemExit("n musí být alespoň 2")
    if not 0 <= percent < 100:
        raise SystemExit("procento překážek musí být od 0 do 100")
    if percent < 40:
        print(f"Pozor: {percent:g} % je méně, než chce zadání (alespoň 40 %).")
    if seed is None:
        seed = random.randrange(10**9)
    return n, seed, percent


def main():
    import time
    n, seed, percent = read_input()
    ratio = percent / 100
    k = math.ceil(ratio * n * n)
    print(f"\nBludiště {n:,} × {n:,} ({n * n:,} polí), {k:,} překážek ({percent:g} %), seed {seed}")

    t0 = time.perf_counter()
    try:
        g = generate_maze(n, ratio=ratio, seed=seed)
    except ValueError as e:
        raise SystemExit(f"Chyba: {e}")
    t1 = time.perf_counter()
    res = bfs(g, n)
    t2 = time.perf_counter()

    if res is None:
        print("Výsledek: cesta NEEXISTUJE – BFS prošlo celou oblast dosažitelnou "
              "ze startu a cíl v ní není.")
    else:
        D, moves = res
        print(f"Výsledek: nejkratší cesta má {D:,} kroků "
              f"(dolní mez 2(n-1) = {2 * (n - 1):,})")
        if n <= 30:
            print()
            print_maze(g, n, moves)
            print()
    print(f"Čas: generování {t1 - t0:.2f} s, BFS {t2 - t1:.2f} s, celkem {t2 - t0:.2f} s")
    mem = peak_memory_mb()
    print(f"Paměť: mřížka {len(g):,} B" + (f", špička procesu ~{mem:.0f} MB" if mem else ""))


if __name__ == "__main__":
    main()