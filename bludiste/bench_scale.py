"""Škálování (volitelná část, +10 b): jak velké n se stihne do 10 minut.

Nejhorší případ pro BFS je mřížka BEZ zdí: BFS navštíví všech n² polí
a s každým udělá nejvíc práce. S překážkami navštíví nejvýš ~60 % polí
(a obvykle mnohem méně), takže čas BFS na prázdné mřížce je HORNÍ MEZ
pro libovolné bludiště velikosti n. K tomu se přičte čas generátoru.

  worst(n) = generování(n, 40 % zdí) + BFS(n, prázdná mřížka)

Použití:
  python3 bench_scale.py                 # odhad n_max pro limit 600 s + ověření
  python3 bench_scale.py --limit 600     # jiný limit v sekundách
  python3 bench_scale.py --n 15000       # změř jen jedno konkrétní n
  python3 bench_scale.py --no-verify     # jen odhad, bez ověřovacího běhu
"""
import argparse
import math
import platform
import resource
import sys
import time

import maze_opt as mo


def peak_rss_mb():
    r = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    return r / 1024 if sys.platform != "darwin" else r / 1024 / 1024


def measure(n, seed=1):
    t0 = time.perf_counter()
    g = mo.generate_maze(n, seed=seed)
    t1 = time.perf_counter()
    res = mo.bfs(g, n)                  # skutečné náhodné bludiště
    t2 = time.perf_counter()
    del g
    e = mo.new_grid(n)
    t3 = time.perf_counter()
    mo.bfs(e, n)                        # nejhorší případ BFS
    t4 = time.perf_counter()
    del e
    return {
        "n": n, "gen": t1 - t0, "bfs_rand": t2 - t1, "bfs_worst": t4 - t3,
        "found": res is not None, "len": res[0] if res else None,
        "worst": (t1 - t0) + (t4 - t3),
    }


def show(r):
    path = f"cesta {r['len']} kroků" if r["found"] else "cesta neexistuje"
    print(f"n={r['n']:>6}  gen {r['gen']:7.1f} s  BFS náhodné {r['bfs_rand']:7.1f} s ({path})"
          f"  BFS nejhorší {r['bfs_worst']:7.1f} s  => nejhorší celkem {r['worst']:7.1f} s"
          f"  | RSS {peak_rss_mb():.0f} MB", flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=float, default=600.0)
    ap.add_argument("--n", type=int)
    ap.add_argument("--no-verify", action="store_true")
    ap.add_argument("--safety", type=float, default=0.9,
                    help="odhad míří na safety × limit (rezerva na pomalejší stroj)")
    a = ap.parse_args()

    print(f"Python {platform.python_version()} | {platform.platform()} | {platform.processor() or platform.machine()}")
    if a.n:
        show(measure(a.n))
        return

    # 1) kalibrace na menších n: čas na jedno pole
    samples = []
    for n in (1000, 2000, 4000):
        r = measure(n)
        show(r)
        samples.append(r)
    per_cell = max(r["worst"] / (r["n"] ** 2) for r in samples)
    n_max = int(math.sqrt(a.safety * a.limit / per_cell))
    n_max -= n_max % 100
    print(f"\n~{per_cell * 1e9:.0f} ns na pole => odhad n_max ≈ {n_max:,} "
          f"(cíl {a.safety:.0%} z limitu {a.limit:.0f} s)\n")

    # 2) ověření skutečným během
    if not a.no_verify:
        r = measure(n_max)
        show(r)
        verdict = "OK, v limitu" if r["worst"] <= a.limit else "PŘEKROČENO"
        print(f"\nn = {n_max:,}: nejhorší případ {r['worst']:.0f} s z {a.limit:.0f} s -> {verdict}")


if __name__ == "__main__":
    main()
