"""Porovnání paměťové náročnosti původní (maze.py) a optimalizované
(maze_opt.py) verze. Měří špičku alokací Pythonu (tracemalloc) během
generování + BFS. Každé měření běží v samostatném procesu.

Použití: python3 bench_memory.py [n1 n2 ...]
"""
import subprocess
import sys

CODE = r"""
import sys, tracemalloc, time
mod, n, seed, empty = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), sys.argv[4] == "1"
M = __import__(mod)
tracemalloc.start()
if empty:
    g = M.new_grid(n) if mod == "maze_opt" else bytearray(n * n)
else:
    g = M.generate_maze(n, seed=seed)
t = time.perf_counter()
r = M.bfs(g, n)
t = time.perf_counter() - t
cur, peak = tracemalloc.get_traced_memory()
print(peak, r is not None, t)
"""


def measure(mod, n, seed=1, empty=False):
    out = subprocess.run(
        [sys.executable, "-c", CODE, mod, str(n), str(seed), "1" if empty else "0"],
        capture_output=True, text=True, check=True,
    ).stdout.split()
    return int(out[0]), out[1] == "True"


def fmt(b):
    for unit in ("B", "kB", "MB", "GB"):
        if b < 1024:
            return f"{b:,.1f} {unit}"
        b /= 1024
    return f"{b:.1f} TB"


if __name__ == "__main__":
    sizes = [int(a) for a in sys.argv[1:]] or [100, 1000, 3000]
    print(f"{'n':>6} {'instance':<12} {'původní':>12} {'optimalizovaná':>16} {'B/pole':>8} {'úspora':>8}")
    for n in sizes:
        for label, empty in (("40 % zdí", False), ("bez zdí", True)):
            a, _ = measure("maze", n, empty=empty)
            b, found = measure("maze_opt", n, empty=empty)
            print(f"{n:>6} {label:<12} {fmt(a):>12} {fmt(b):>16} {b / (n * n):>8.3f} {a / b:>7.0f}×")
