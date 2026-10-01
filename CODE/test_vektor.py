"""test_vektor.py — K8: UZAY kademesi. Sentetik, deterministik."""
import os, sys, numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from vektor import (hv, bind, bundle, benzerlik, token_vek, sorgula,
                    adim_vek, dizi_vek, sahne_vek, icinde_mi, BOYUT)

G, K = [], []
def kontrol(ad, sart, detay=""):
    (G if sart else K).append(ad)
    print(f"   {'GECTI' if sart else 'KALDI':<6} {ad}" + (f"   {detay}" if detay else ""))

print("="*74); print("K8 — UZAY (vektor temsili)"); print("="*74)

a, b = hv("A"), hv("B")
kontrol("iki rastgele hipervektor neredeyse DIK", abs(benzerlik(a,b)) < 0.10,
        f"benz={benzerlik(a,b):+.3f}")
kontrol("ayni anahtar -> AYNI vektor (kalici)", benzerlik(hv("A"), a) > 0.9999)
kontrol("bind benzerligi YOK EDER", abs(benzerlik(bind(a,b), a)) < 0.10,
        f"benz={benzerlik(bind(a,b),a):+.3f}")
kontrol("bind kendi tersi: (a*b)*b = a", benzerlik(bind(bind(a,b),b), a) > 0.9999)
c = hv("C")
bnd = bundle([a,b,c])
kontrol("bundle uyelige BENZER", min(benzerlik(bnd,x) for x in (a,b,c)) > 0.4,
        f"min={min(benzerlik(bnd,x) for x in (a,b,c)):.2f}")
kontrol("bundle uye OLMAYANA benzemez", abs(benzerlik(bnd, hv("Z"))) < 0.15,
        f"benz={benzerlik(bnd,hv('Z')):+.3f}")

print()
# --- token benzerligi DERECELI mi? asil mesele bu ---
t0 = (3, 1, 1, 2, 1, 0, "-", 0, 0, 1, 0)
t_ayni  = (3, 1, 1, 2, 1, 0, "-", 0, 0, 1, 0)
t_1fark = (3, 1, 1, 2, 1, 0, "-", 0, 1, 1, 0)          # 1 alan farkli
t_2fark = (3, 1, 2, 2, 1, 0, "-", 0, 1, 1, 0)          # 2 alan farkli
t_hepsi = (9, 4, 4, 5, 0, 2, "yatay", 1, 1, 0, 1)      # hepsi farkli
s = lambda x: benzerlik(token_vek(t0), token_vek(x))
kontrol("ayni token -> benzerlik 1.0", s(t_ayni) > 0.9999)
kontrol("1 alan farkli -> YUKSEK benzerlik", s(t_1fark) > 0.70, f"{s(t_1fark):.2f}")
kontrol("2 alan farkli -> daha dusuk ama hala anlamli",
        s(t_1fark) > s(t_2fark) > 0.45, f"{s(t_2fark):.2f}")
kontrol("hepsi farkli -> benzerlik ~0", abs(s(t_hepsi)) < 0.25, f"{s(t_hepsi):+.2f}")
kontrol("benzerlik SIRALI: ayni > 1fark > 2fark > hepsi",
        0.9999 < s(t_ayni) and s(t_ayni) > s(t_1fark) > s(t_2fark) > abs(s(t_hepsi)))

print()
# --- UZAYA GIRIP CIKMA: sorgu ---
v = token_vek(t0)
kontrol("sorgu: 'rengi ne?' dogru cevap", sorgula(v, "renk", [0,3,5,9]) == 3)
kontrol("sorgu: 'alani ne?'", sorgula(v, "alan", [0,1,2,3,4,5]) == 2)
kontrol("sorgu: 'kare mi?'", sorgula(v, "kare", [0,1]) == 1)

print()
# --- DIZI (cukur govdesi) ---
tA, tB = t0, t_hepsi
d1 = dizi_vek([(tA,3),(tB,1)])
d2 = dizi_vek([(tA,3),(tB,1)])
d3 = dizi_vek([(tB,1),(tA,3)])          # ayni adimlar, TERS SIRA
d4 = dizi_vek([(tA,3),(tB,2)])          # son eylem farkli
kontrol("ayni dizi -> ayni vektor", benzerlik(d1,d2) > 0.9999)
kontrol("SIRA onemli: [A,B] != [B,A]", benzerlik(d1,d3) < 0.35,
        f"benz={benzerlik(d1,d3):+.2f}")
kontrol("tek eylem farkli -> kismen benzer",
        0.25 < benzerlik(d1,d4) < 0.85, f"benz={benzerlik(d1,d4):.2f}")

print()
# --- SAHNE uyeligi (cukur girisi icin) ---
sv = sahne_vek([t0, t_hepsi, t_2fark])
kontrol("sahnedeki nesne bulunur", icinde_mi(sv, t0))
kontrol("sahnede OLMAYAN bulunmaz", not icinde_mi(sv, (7,7,7,7,7,7,"x",1,1,1,1)),
        "(bu token uyelerle 4 alan paylasiyor -> tam ilgisiz degil, 0.26)")
kontrol("sahnedekine BENZER nesne de bulunur (tam esitlik gerekmiyor)",
        icinde_mi(sv, t_1fark), "<-- tam esitlikte KACIRILIRDI")

print()
print("="*74); print(f"SONUC: {len(G)} gecti, {len(K)} kaldi")
for k in K: print("   -", k)
print("="*74)
sys.exit(1 if K else 0)
