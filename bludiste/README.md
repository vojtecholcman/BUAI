# Nejkratší cesta v bludišti – BFS

**Zadání:** mřížka n×n, start (0, 0), cíl (n−1, n−1), náhodně rozmístěné překážky velikosti jednoho pole, jejich počet je alespoň 0,4·n². Úkolem je najít nejkratší cestu, pokud existuje, a v opačném případě dokázat, že neexistuje. Povinná velikost je n = 100.

**Předpoklady:** pohyb ve 4-okolí (nahoru, dolů, doleva, doprava), každý krok stojí 1. Překážek je přesně ⌈0,4·n²⌉, start a cíl jsou vždy volné.

## Soubory a spuštění

| soubor | obsah |
|---|---|
| `maze.py` | základní řešení: generátor, BFS, výpis bludiště |
| `maze_opt.py` | paměťově optimalizované řešení (2 bity na pole) |
| `test_maze.py`, `test_opt.py` | testy správnosti |
| `bench_memory.py` | měření paměti: původní vs. optimalizovaná verze |
| `bench_scale.py` | test škálování s limitem 10 min |
| `bench_thinkpad.txt` | výstup `bench_scale.py` na referenčním počítači |

Stačí Python 3, bez externích knihoven.

```bash
python3 maze.py                 # ukázka: n = 10 a n = 100
python3 maze_opt.py 100 [seed]  # optimalizovaná verze, libovolné n
python3 test_maze.py && python3 test_opt.py
python3 bench_scale.py          # největší n do 10 min
```

## 1. Řešení (n = 100)

**Stavový prostor:** stav je volné pole. Přechod vede na sousední volné pole. Počáteční stav je (0, 0), cílový (n−1, n−1).

**Algoritmus: prohledávání do šířky (BFS).** Všechny přechody mají stejnou cenu, takže BFS prochází stavy v pořadí podle vzdálenosti od startu. Cíl tedy poprvé dosáhne nejkratší cestou. Pro každé pole si pamatujeme, odkud jsme do něj přišli, a cestu pak zrekonstruujeme zpětně od cíle. Pole označíme jako navštívené už při vložení do fronty, takže se každé pole zpracuje nejvýš jednou. Čas je O(n²) a paměť O(n²).

**Generátor:** vybere ⌈0,4·n²⌉ různých polí z polí mimo start a cíl. Ve verzi `maze_opt.py` se losuje přímo do mřížky s odmítnutím už obsazených polí. Generátor bere `seed`, takže instance jdou reprodukovat.

**Výsledky (n = 100):**
- `seed = 114`: nejkratší cesta má 256 kroků, nalezena za ~3 ms.
- `seed = 0`: cesta neexistuje, protože start je zazděný.
- `maze_opt.py` losuje jinak, takže stejný seed dá jiné bludiště: `python3 maze_opt.py 100 26` má cestu dlouhou 226 kroků.
- Cestu má jen asi **1,4 %** náhodných instancí (14 z 1000). Pro n = 10 je to asi 11 %. Příčina: 40 % překážek leží těsně pod perkolačním prahem čtvercové mřížky (~40,7 % překážek). Navíc start a cíl jsou v rozích, kde mají jen 2 sousedy, a snadno je zazdí. Výstup „cesta neexistuje“ je proto běžný a správný výsledek.

## 2. Důkaz korektnosti

Bludiště chápeme jako neorientovaný graf: vrcholy jsou volná pole, hrany vedou mezi sousedními volnými poli. Označme δ(v) délku nejkratší cesty ze startu s do v a d(v) délku řetězce rodičů z v zpět do s.

1. **Konečnost.** Vrchol se vloží do fronty jen tehdy, když ještě není navštíven, a tím se hned označí. Proto je ve frontě nejvýš jednou a algoritmus skončí po nejvýš n² krocích.
2. **d(v) ≥ δ(v).** Řetězec rodičů je skutečná cesta v grafu, protože rodič je vždy volný soused.
3. **Monotonie fronty.** Ve frontě jsou vrcholy seřazené neklesajícím d a rozdíl mezi prvním a posledním je nejvýš 1. Plyne to indukcí: vrchol w přidaný při zpracování u má d(w) = d(u) + 1.
4. **Úplnost.** Každý vrchol dosažitelný ze startu bude navštíven. Indukcí podle δ(v): předchůdce u na nejkratší cestě do v je navštíven a při jeho zpracování se navštíví i v.
5. **Optimalita, d(v) = δ(v).** Sporem: vezměme v s nejmenším δ(v), pro které d(v) > δ(v), a jeho předchůdce u na nejkratší cestě. Pro u platí d(u) = δ(u). Když se zpracuje u, je v buď ještě nenavštívený a dostane d(v) = d(u) + 1 = δ(v), nebo byl vložen dřív a z bodu 3 plyne d(v) ≤ d(u) + 1 = δ(v). Obě možnosti jsou spor.

**Závěr.** Pokud cesta existuje, BFS podle bodu 4 dosáhne cíle a podle bodu 5 vrátí nejkratší cestu. Pokud se fronta vyprázdní a cíl nebyl dosažen, BFS prošlo celou komponentu souvislosti startu a cíl v ní není. To je **důkaz, že cesta neexistuje** (jinak by byl cíl navštíven podle bodu 4).

**Ověření testy:**
- Každá nalezená cesta se kontroluje: začíná ve startu, končí v cíli, vede jen přes sousední volná pole.
- 1200 malých instancí (n ≤ 6) se porovnává s brute force, které projde všechny cesty.
- 405 instancí do n = 100 se porovnává s nezávislým Bellman-Fordem.
- Optimalizovaná verze dává na ~2100 instancích stejné výsledky jako základní.

## 3. Optimalizace paměti (volitelná část)

Celý stav BFS je uložený ve **2 bitech na pole**, tedy 4 pole na bajt. Každé pole má jeden ze 4 stavů:

| hodnota | význam |
|---|---|
| 0 | volné, nenavštívené |
| 1 | překážka |
| 2 | navštívené, b = 0 |
| 3 | navštívené, b = 1 |

kde b = ⌊d/2⌋ mod 2 a d je vzdálenost od startu.

**Proč k rekonstrukci cesty stačí jeden bit b místo ukazatele na rodiče:** mřížka je bipartitní (šachovnice), takže vzdálenosti sousedních polí se liší přesně o 1. Navštívený soused pole se vzdáleností d má tedy vzdálenost buď d−1, nebo d+1. Pro tato dvě čísla má ⌊·/2⌋ různou paritu, takže se liší v bitu b. Podle b proto poznáme, který soused leží blíž ke startu, a dojdeme zpětně z cíle do startu.

**Další úspory:**
- generátor nevytváří pomocný seznam všech n² polí,
- BFS drží jen aktuální a příští vrstvu jako kompaktní pole `array('I')` se 4 B na prvek,
- cesta se ukládá jako směry, 1 B na krok.

| n | původní (`maze.py`) | optimalizovaná | B / pole | úspora |
|---|---|---|---|---|
| 100 | 427 kB | 5,6 kB | 0,58 | 76× |
| 1 000 | 42 MB | 247 kB | 0,25 | 174× |
| 3 000 | 379 MB | 2,1 MB | 0,25 | 177× |

Měřeno nástrojem `tracemalloc` jako špička během generování a BFS (`bench_memory.py`). Rychlost zůstala stejná.

## 4. Škálování (volitelná část)

Úzkým hrdlem je **čas, ne paměť**: i pro n = 20 000 zabere mřížka jen 100 MB.

**Nejhorší případ:** jako horní mez bereme mřížku **bez překážek**, kde BFS navštíví všech n² polí. S překážkami navštíví nejvýš ~60 % polí a obvykle mnohem méně. `bench_scale.py` proto měří čas generátoru (40 % překážek) a k němu přičte čas BFS na prázdné mřížce. Na menších n zkalibruje cenu jednoho pole, odhadne největší n, které se vejde do limitu, a ověří ho skutečným během.

**Referenční počítač** (místo počítačů učebny P3):

| | |
|---|---|
| notebook | Lenovo ThinkPad T14 Gen 1 |
| CPU | AMD Ryzen 5 PRO 4650U (6 jader / 12 vláken, program běží na 1 jádře) |
| RAM | 7 GB |
| systém | Debian GNU/Linux 13 (trixie), jádro Linux 6.12, x86_64 |
| Python | 3.13.5, jen standardní knihovna |

**Výsledek** (`bench_thinkpad.txt`):

| n | generování | BFS (nejhorší případ) | celkem | paměť (RSS) |
|---|---|---|---|---|
| 1 000 | 0,5 s | 1,2 s | 1,7 s | 13 MB |
| 2 000 | 2,0 s | 4,5 s | 6,5 s | 14 MB |
| 4 000 | 7,6 s | 17,7 s | 25,3 s | 18 MB |
| **17 800** | 142,8 s | 314,6 s | **457 s** | 92 MB |

Kalibrace vyšla na ~1,7 µs na pole, z toho odhad n_max ≈ 17 800 (cíl 90 % limitu). Ověřovací běh pro **n = 17 800 (3,17·10⁸ polí) trval 457 s, tedy v limitu 10 min**. Rozhoduje hlavně rychlost jednoho jádra CPU, na jiném počítači se výsledek může lišit.

## Použité prompty (AI asistent)

Použitý model: **Claude Opus 5.5** (Anthropic).

Při vypracování jsem postupoval s AI asistentem krok po kroku. Kód jsem nechal doplnit, prošel a otestoval. Prompty, které stačí k zopakování postupu:

1. *„Mám zadání: [zadání]. Proveď mě řešením krok po kroku – rozbor, volba algoritmu, plán.“*
2. *„Napiš v Pythonu generátor bludiště n×n jako 1D bytearray s přesně ⌈0,4·n²⌉ překážkami, start a cíl volné, volitelný seed, a funkci pro výpis.“*
3. *„Doplň BFS, které vrátí nejkratší cestu jako seznam indexů nebo None, vysvětli hlídání okrajů mřížky a rekonstrukci cesty.“*
4. *„Napiš testy správnosti: validace cesty, porovnání s brute-force na malých mřížkách a s nezávislým algoritmem na větších.“*
5. *„Sepiš formální důkaz, že BFS najde nejkratší cestu a že prázdná fronta dokazuje neexistenci cesty.“*
6. *„Optimalizuj paměť na minimum – kolik bitů na pole je potřeba? Změř původní a novou verzi.“*
7. *„Napiš benchmark, který najde největší n spočitatelné do 10 minut v nejhorším případě, a změř ho.“*
