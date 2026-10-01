"""test_hafiza.py — K17-K19: hafiza ve israr."""
import sys, os, shutil, tempfile
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from hafiza import Hafiza, Israrci

G, K = [], []
def kontrol(ad, sart, detay=""):
    (G if sart else K).append(ad)
    print(f"   {'GECTI' if sart else 'KALDI':<6} {ad}" + (f"   {detay}" if detay else ""))

TEST = os.path.join(tempfile.gettempdir(), "brain_hafiza_test")
shutil.rmtree(TEST, ignore_errors=True)
A, B = ("tokA",), ("tokB",)

print("="*74); print("K17 — HAFIZA (oyuna ozel, diskte kalici)"); print("="*74)
h = Hafiza("test1", TEST)
h.yaz(1, A, 3, 10.0, 0)
h.yaz(2, A, 3, 8.0, 0)
h.yaz(3, B, 1, 0.0, 0)
kontrol("her eylem TUM hafizaya yaziliyor", len(h.tum) == 3)
kontrol("degisim ureten AYRI hafizaya", h.ise_yarar_mi(A, 3) == 9.0,
        f"ort={h.ise_yarar_mi(A,3)}")
kontrol("degisim URETMEYEN ayri hafizada yok", h.ise_yarar_mi(B, 1) == 0.0)
kontrol("en iyiler sirali", h.en_iyiler()[0][2] == (A, 3))

h.kaydet()
kontrol("hafiza.txt diske yazildi", os.path.exists(f"{TEST}/test1.txt"))
kontrol("ise_yarayan.txt diske yazildi",
        os.path.exists(f"{TEST}/test1_ise_yarayan.txt"))
h2 = Hafiza("test1", TEST)
kontrol("ONCEKI KOSUDAN devraliyor", h2.yukle() and h2.ise_yarar_mi(A, 3) == 9.0)
h3 = Hafiza("baska_oyun", TEST)
kontrol("HER OYUN ICIN AYRI hafiza", not h3.yukle() and h3.ise_yarar_mi(A, 3) == 0.0)

print()
print("="*74); print("K18 — SEVIYE RECETESI (son hale goturen adimlar)"); print("="*74)
h4 = Hafiza("test2", TEST, recete_uzunluk=3)
for i, (tk, e) in enumerate([(A,1),(B,2),(A,3),(B,4),(A,5)]):
    h4.yaz(i, tk, e, 1.0, 0)
r = h4.seviye_atladi()
kontrol("recete = seviyeyi geciren SON adimlar", r == [(A,3),(B,4),(A,5)], f"{r}")
kontrol("recete kaydedildi", len(h4.receteler) == 1)
h4.yaz(6, B, 6, 1.0, 1)
r2 = h4.seviye_atladi()
kontrol("ikinci seviye ikinci recete", len(h4.receteler) == 2 and r2 == [(B,6)])
kontrol("butun receteler birlestirilebiliyor",
        h4.recete_adimlari() == [(A,3),(B,4),(A,5),(B,6)])
h4.kaydet()
kontrol("recete.txt diske yazildi", os.path.exists(f"{TEST}/test2_recete.txt"))

print()
print("="*74); print("K19 — ISRAR ('insan eylemi sona kadar goturur')"); print("="*74)
iz = Israrci(sabir=2)
kontrol("baslangicta israr yok", iz.onerir({A: 1, B: 1}) is None)
iz.bildir((A, 3), 10.0)
kontrol("degisim ureten eylem ISRAR EDILIYOR", iz.onerir({(A,3): 1}) == (A,3))
iz.bildir((A, 3), 5.0)
kontrol("degisim surdukce israr surer", iz.onerir({(A,3): 1}) == (A,3))
iz.bildir((A, 3), 0.0)
kontrol("tek bos adim -> hala israr (sabir=2)", iz.onerir({(A,3): 1}) == (A,3))
iz.bildir((A, 3), 0.0)
kontrol("TUKENDI -> israr birakiliyor", iz.onerir({(A,3): 1}) is None,
        "<-- salinim yerine sona kadar goturup birakma")
iz2 = Israrci(sabir=2)
iz2.bildir((A, 3), 10.0)
kontrol("nesne sahneden kalkarsa israr birakilir",
        iz2.onerir({(B,1): 1}) is None)
iz3 = Israrci(sabir=2, ust_sinir=3)
for _ in range(3):
    iz3.bildir((A, 3), 5.0)
kontrol("ust sinir: sonsuza kadar israr etmez", iz3.onerir({(A,3): 1}) is None)

shutil.rmtree(TEST, ignore_errors=True)
print()
print("="*74); print(f"SONUC: {len(G)} gecti, {len(K)} kaldi")
for k in K: print("   -", k)
print("="*74)
sys.exit(1 if K else 0)
