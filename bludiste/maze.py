import math
import random
from collections import deque

FREE = 0
WALL = 1


def generate_maze(n, ratio=0.4, seed=None):
    """Vrátí bytearray délky n*n, kde WALL = překážka.
    Start (index 0) a cíl (index n*n-1) zůstávají volné.
    Počet překážek = ceil(ratio * n*n)."""
    if n < 2:
        raise ValueError("n musí být alespoň 2 (start a cíl musí být různá pole)")

    rng = random.Random(seed)
    k = math.ceil(ratio * n * n)
    grid = bytearray(n * n)  # vše FREE

    # 1) kontrola: k dispozici je n*n - 2 polí (start a cíl musí být volné)
    available = n * n - 2
    if k > available:
        raise ValueError(f"{k} překážek se nevejde do {available} volných polí")

    # 2) k RŮZNÝCH indexů z rozsahu 1 .. n*n-2 (vynechává start 0 i cíl n*n-1)
    walls = rng.sample(range(1, n * n - 1), k)

    # 3) nastavení překážek
    for i in walls:
        grid[i] = WALL

    return grid


def print_maze(grid, n, path=None):
    """Vypíše bludiště: '#' překážka, '.' volno, 'S' start, 'G' cíl, '*' cesta."""
    on_path = set(path) if path else set()
    start, goal = 0, n * n - 1
    for y in range(n):
        row = []
        for x in range(n):
            i = y * n + x
            if i == start:
                row.append("S")
            elif i == goal:
                row.append("G")
            elif grid[i] == WALL:
                row.append("#")
            elif i in on_path:
                row.append("*")
            else:
                row.append(".")
        print(" ".join(row))


def bfs(grid, n):
    """Prohledávání do šířky ze startu (index 0) do cíle (index n*n-1).
    Vrátí nejkratší cestu jako seznam indexů od startu do cíle,
    nebo None, pokud cesta neexistuje."""
    start, goal = 0, n * n - 1

    # parent[i] = index pole, ze kterého jsme do i poprvé přišli
    # -1 znamená "zatím nenavštíveno"; start je svým vlastním rodičem
    parent = [-1] * (n * n)
    parent[start] = start

    queue = deque([start])

    while queue:
        i = queue.popleft()

        if i == goal:
            # rekonstrukce cesty: jdeme po rodičích zpět ke startu
            path = [goal]
            while path[-1] != start:
                path.append(parent[path[-1]])
            path.reverse()
            return path

        x = i % n
        # sousedé ve 4-okolí; podmínky hlídají okraje mřížky
        neighbors = []
        if i >= n:          # nahoru (nejsme v prvním řádku)
            neighbors.append(i - n)
        if i < n * n - n:   # dolů (nejsme v posledním řádku)
            neighbors.append(i + n)
        if x > 0:           # doleva (nejsme v prvním sloupci)
            neighbors.append(i - 1)
        if x < n - 1:       # doprava (nejsme v posledním sloupci)
            neighbors.append(i + 1)

        for j in neighbors:
            if grid[j] == FREE and parent[j] == -1:
                parent[j] = i
                queue.append(j)

    # fronta je prázdná a cíl nebyl dosažen => cesta neexistuje
    return None


def solve_and_report(n, seed, show=False):
    import time
    grid = generate_maze(n, seed=seed)
    t0 = time.perf_counter()
    path = bfs(grid, n)
    t = time.perf_counter() - t0

    if show:
        print_maze(grid, n, path)
    if path is None:
        print(f"n={n}, seed={seed}: cesta NEEXISTUJE  ({t*1000:.2f} ms)")
    else:
        print(f"n={n}, seed={seed}: nejkratší cesta má {len(path) - 1} kroků  ({t*1000:.2f} ms)")
    return path


if __name__ == "__main__":
    # malá ukázka: instance bez cesty a instance s cestou
    solve_and_report(10, seed=42, show=True)
    print()
    solve_and_report(10, seed=8, show=True)
    print()

    # zadání: n = 100 — instance s cestou a bez cesty
    solve_and_report(100, seed=114)
    solve_and_report(100, seed=0)

    # jak často cesta vůbec existuje (perkolační práh)
    trials = 1000
    found = sum(bfs(generate_maze(100, seed=s), 100) is not None for s in range(trials))
    print(f"\nCesta existovala v {found} z {trials} instancí n=100.")
