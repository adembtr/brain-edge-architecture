"""test_model.py — K13-K15: TEK GOZLEM -> COK TAHMIN."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from model import UzaysalModel

G, K = [], []
def kontrol(ad, sart, detay=""):
    (G if sart else K).append(ad)
    print(f"   {'GECTI' if sart else 'KALDI':<6} {ad}" + (f"   {detay}" if detay else ""))

A       = (3, 1, 1, 2, 1, 0, "-", 0, 0, 1, 0)
A_1fark = (3, 1, 1, 2, 1, 0, "-", 0, 1, 1, 0)
A_2fark = (3, 1, 2, 2, 1, 0, "-", 0, 1, 1, 0)
B       = (9, 4, 4, 5, 0, 2, "yatay", 1, 1, 0, 1)
E1, E2 = ("deg", 1), ("deg", 3)

print("="*74); print("K13 — TEK GOZLEM -> NESNE uzerinden tahmin"); print("="*74)
m = UzaysalModel()
m.gozle(A, 3, E1)                       # TEK gozlem
e, g, kay = m.tahmin(A, 3)
kontrol("kendi kaydi geri geliyor", e == E1 and kay == "kendi", f"guven={g:.2f}")

e, g, kay = m.tahmin(A_1fark, 3)
kontrol("HIC DENENMEMIS benzer token -> TAHMIN VAR",
        e == E1 and kay == "nesne", f"{e} guven={g:.2f} kaynak={kay}")
e, g, kay = m.tahmin(A_2fark, 3)
kontrol("2 alan farkli token -> tahmin var", e == E1 and kay == "nesne")
e, g, kay = m.tahmin(B, 3)
kontrol("ILGISIZ token -> tahmin YOK (uydurmuyor)", e is None, f"{e}")
e, g, kay = m.tahmin(A_1fark, 1)
kontrol("baska eylem, hic veri yok -> tahmin YOK", e is None)

print()
print("="*74); print("K14 — CELISKI ve COGUNLUK"); print("="*74)
m2 = UzaysalModel()
for _ in range(3):
    m2.gozle(A, 3, E1)
m2.gozle(A_1fark, 3, E2)
e, g, kay = m2.tahmin(A_2fark, 3)
kontrol("iki benzer kaynak celisiyorsa cogunluk kazanir",
        e in (E1, E2), f"{e} guven={g:.2f}")
kontrol("celiskide guven 1.0 DEGIL", g < 0.99, f"guven={g:.2f}")
m3 = UzaysalModel()
m3.gozle(A, 3, E1); m3.gozle(A, 3, E1); m3.gozle(A, 3, E2)
e, g, kay = m3.tahmin(A, 3)
kontrol("kendi kaydinda cogunluk", e == E1 and abs(g - 2/3) < 0.01, f"guven={g:.2f}")

print()
print("="*74); print("K15 — EYLEM BENZERLIGI (eylemin ne oldugu SOYLENMIYOR)"); print("="*74)
m4 = UzaysalModel()
# eylem 1 ve 2 ayni etkiyi uretiyor; eylem 5 farkli
for tk in (A, A_2fark, B):
    m4.gozle(tk, 1, E1)
    m4.gozle(tk, 2, E1)
    m4.gozle(tk, 5, E2)
b12 = m4.eylem_benzerligi(1, 2)
b15 = m4.eylem_benzerligi(1, 5)
kontrol("ayni etkiyi ureten eylemler BENZER", b12 > 0.85, f"benz(1,2)={b12:.2f}")
kontrol("farkli etki ureten eylemler benzer DEGIL", b15 < 0.35, f"benz(1,5)={b15:.2f}")
kontrol("eylem benzerligi SIRALI", b12 > b15)

C = (5, 2, 2, 3, 1, 0, "-", 0, 0, 0, 1)
m5 = UzaysalModel()
for tk in (A, B):
    m5.gozle(tk, 1, E1); m5.gozle(tk, 2, E1)
m5.gozle(C, 1, E2)                       # C icin SADECE eylem 1 denendi
e, g, kay = m5.tahmin(C, 2)              # eylem 2 hic denenmedi
kontrol("benzer EYLEM uzerinden tahmin", e is not None,
        f"{e} kaynak={kay} guven={g:.2f}")

print()
print("="*74); print("K16 — KAPSAMA: tek gozlem kac cifti aciyor"); print("="*74)
m6 = UzaysalModel()
tokenlar = [A, A_1fark, A_2fark, B, C]
eylemler = [1, 2, 3, 5]
t0, d0, p0 = m6.kapsama(tokenlar, eylemler)
kontrol("bos model -> hicbir tahmin yok", d0 == 0 and p0 == 0, f"{t0} cift")
m6.gozle(A, 3, E1)
t1, d1, p1 = m6.kapsama(tokenlar, eylemler)
kontrol("TEK gozlem birden fazla cifti aciyor", p1 >= 2,
        f"1 gozlem -> {d1} denenmis + {p1} TAHMIN = {d1+p1}/{t1}")
for a in eylemler:
    m6.gozle(A, a, E1)
t2, d2, p2 = m6.kapsama(tokenlar, eylemler)
kontrol("tek token'da tum eylemler -> kapsama buyur",
        (d2 + p2) > (d1 + p1), f"{d2}+{p2}={d2+p2}/{t2}")

print()
print("="*74); print(f"SONUC: {len(G)} gecti, {len(K)} kaldi")
for k in K: print("   -", k)
print("="*74)
sys.exit(1 if K else 0)
