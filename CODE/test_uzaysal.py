"""test_uzaysal.py — K9-K12: uzayin BAGLANMASI. Sentetik, deterministik."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from uzaysal import UzaysalKredi, giris_uygun, sahne_benzerligi
from vektor import token_vek, benzerlik

G, K = [], []
def kontrol(ad, sart, detay=""):
    (G if sart else K).append(ad)
    print(f"   {'GECTI' if sart else 'KALDI':<6} {ad}" + (f"   {detay}" if detay else ""))

A       = (3, 1, 1, 2, 1, 0, "-", 0, 0, 1, 0)
A_1fark = (3, 1, 1, 2, 1, 0, "-", 0, 1, 1, 0)     # benz ~0.74
A_2fark = (3, 1, 2, 2, 1, 0, "-", 0, 1, 1, 0)     # benz ~0.64
B       = (9, 4, 4, 5, 0, 2, "yatay", 1, 1, 0, 1) # benz ~0.00

print("="*74); print("K9 — KREDI TRANSFERI (tam esitlik yerine benzerlik)"); print("="*74)
kr = UzaysalKredi()
for _ in range(6):
    kr.yaz("birlestir", A, 3, iyi=True)
kendi = kr.oku("birlestir", A, 3)
kontrol("ogrenilen token'in kredisi yukseldi", kendi > 0.85, f"{kendi:.2f}")

t1 = kr.oku("birlestir", A_1fark, 3)
kontrol("HIC DENENMEMIS benzer token kredi DEVRALIYOR", t1 > 0.80,
        f"{t1:.2f}  <-- tam esitlikte 0.50 kalirdi")
t2 = kr.oku("birlestir", A_2fark, 3)
kontrol("2 alan farkli token da devraliyor", t2 > 0.80, f"{t2:.2f}")
tb = kr.oku("birlestir", B, 3)
kontrol("ILGISIZ token devralmiyor", abs(tb - 0.5) < 0.01,
        f"{tb:.2f}  <-- varsayilanda kaliyor")

kb = kr.oku("birlestir", A_1fark, 1)
kontrol("BASKA EYLEM icin kredi sizmiyor", abs(kb - 0.5) < 0.01, f"{kb:.2f}")
kt = kr.oku("temizle", A_1fark, 3)
kontrol("BASKA HIPOTEZ TURU icin kredi sizmiyor", abs(kt - 0.5) < 0.01, f"{kt:.2f}")

print()
print("="*74); print("K10 — KOTU DENEYIM DE TRANSFER OLUYOR MU"); print("="*74)
kr2 = UzaysalKredi()
for _ in range(10):
    kr2.yaz("birlestir", A, 3, iyi=False)
d = kr2.oku("birlestir", A, 3)
kontrol("ise yaramayan token'in kredisi dustu", d < 0.15, f"{d:.2f}")
d1 = kr2.oku("birlestir", A_1fark, 3)
kontrol("benzer token de dusuk devraliyor (bosa denemez)", d1 < 0.25, f"{d1:.2f}")
db = kr2.oku("birlestir", B, 3)
kontrol("ilgisiz token etkilenmiyor", abs(db - 0.5) < 0.01, f"{db:.2f}")

print()
print("="*74); print("K11 — CUKUR GIRISI BENZERLIKLE"); print("="*74)
kontrol("tam ayni sahne -> uygun", giris_uygun([A], [A, B]))
kontrol("BENZER nesne varsa -> uygun", giris_uygun([A], [A_1fark, B]),
        "<-- tam alt kumede KACIRILIRDI")
kontrol("ilgisiz sahne -> uygun DEGIL", not giris_uygun([A], [B]))
kontrol("iki giris tokenindan biri yoksa -> uygun DEGIL",
        not giris_uygun([A, B], [A_1fark]))
kontrol("bos giris -> her zaman uygun", giris_uygun([], [B]))
kontrol("bos sahne -> uygun degil", not giris_uygun([A], []))

print()
print("="*74); print("K12 — SAHNE BENZERLIGI"); print("="*74)
s1 = sahne_benzerligi([A, B], [A, B])
s2 = sahne_benzerligi([A, B], [A_1fark, B])
s3 = sahne_benzerligi([A, B], [B])
kontrol("ayni sahne -> ~1.0", s1 > 0.99, f"{s1:.2f}")
kontrol("benzer sahne -> yuksek", s2 > 0.60, f"{s2:.2f}")
kontrol("eksik sahne -> daha dusuk", s3 < s2, f"{s3:.2f} < {s2:.2f}")
kontrol("sahne benzerligi SIRALI", s1 > s2 > s3)

print()
print("="*74); print(f"SONUC: {len(G)} gecti, {len(K)} kaldi")
for k in K: print("   -", k)
print("="*74)
sys.exit(1 if K else 0)
