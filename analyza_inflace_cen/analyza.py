# Volitelne rozsireni - indexy spotrebitelskych cen (CSU, tabulka CEN0101ET01)
# potreba: pip install pandas matplotlib
# soubor ceny.csv musi byt ve stejne slozce jako skript

import pandas as pd
import matplotlib.pyplot as plt

# nacteni dat z CSU
df = pd.read_csv("ceny.csv")

# v souboru je vsechno (Praha, duchodci, ruzne typy indexu...)
# vyberu jen index 2015 = 100, cele Cesko, vsechny domacnosti
df = df[df["Typ indexu"] == "Bazický index (2015 = 100)"]
df = df[df["Území"] == "Česko"]
df = df[df["Skupiny domácností"] == "Domácnosti celkem"]

# predelam na tabulku: radky = roky, sloupce = kategorie
tabulka = df.pivot(index="Roky", columns="Klasifikace COICOP 2018-Oddíl", values="Hodnota")


# ---------- 1) graf pro 2 kategorie ----------
kat1 = "Stravovací a ubytovací služby"
kat2 = "Doprava"

plt.figure(figsize=(9, 5))
plt.plot(tabulka.index, tabulka[kat1], marker="o", label=kat1)
plt.plot(tabulka.index, tabulka[kat2], marker="o", label=kat2)
plt.title("Vývoj cen (2015 = 100)")
plt.xlabel("rok")
plt.ylabel("index")
plt.xticks(tabulka.index)
plt.grid(True)
plt.legend()
plt.savefig("graf_porovnani.png")
plt.show()

# o kolik zdrazily od 2015 (index 2025 - 100)
zdrazeni1 = tabulka.loc[2025, kat1] - 100
zdrazeni2 = tabulka.loc[2025, kat2] - 100
print(kat1, "zdrazilo od 2015 o", round(zdrazeni1, 1), "%")
print(kat2, "zdrazila od 2015 o", round(zdrazeni2, 1), "%")

if zdrazeni1 > zdrazeni2:
    print("Vic zdrazila kategorie:", kat1)
else:
    print("Vic zdrazila kategorie:", kat2)


# ---------- 2) mezirocni zmena - Pojisteni a financni sluzby ----------
pojisteni = tabulka["Pojištění a finanční služby"]

# (letos / loni - 1) * 100, shift(1) posune radu o jeden rok dolu = "loni"
zmena = (pojisteni / pojisteni.shift(1) - 1) * 100
zmena = zmena.round(1)

print()
print("Mezirocni zmena - Pojisteni a financni sluzby (%):")
print(zmena.dropna())   # 2015 nema predchozi rok, tak ho vynecham

plt.figure(figsize=(9, 5))
plt.bar(zmena.index[1:], zmena.iloc[1:], color="tab:green")
plt.title("Pojištění a finanční služby – meziroční změna")
plt.xlabel("rok")
plt.ylabel("změna v %")
plt.xticks(zmena.index[1:])
plt.axhline(0, color="black")
plt.savefig("graf_pojisteni.png")
plt.show()


# ---------- 3) kategorie s nejvetsim poklesem od 2015 ----------
# protoze 2015 = 100, rozdil indexu je rovnou zmena v %
zmena_od_2015 = tabulka.loc[2025] - tabulka.loc[2015]
zmena_od_2015 = zmena_od_2015.drop("Úhrn")    # uhrn neni kategorie
zmena_od_2015 = zmena_od_2015.sort_values()   # serazeni od nejmensi

print()
print("Zmena cen 2015 -> 2025 (%), serazeno:")
print(zmena_od_2015)

nejvetsi_pokles = zmena_od_2015.index[0]
print()
print("Nejvetsi pokles ma:", nejvetsi_pokles, zmena_od_2015.iloc[0], "%")
print("Nejlevnejsi byla v roce", tabulka[nejvetsi_pokles].idxmin(),
      "s indexem", tabulka[nejvetsi_pokles].min())