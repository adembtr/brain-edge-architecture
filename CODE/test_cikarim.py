"""test_cikarim.py — K24-K26: cift yonlu cikarim."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from cikarim import Cikarim

G, K = [], []
def kontrol(ad, sart, detay=""):
    (G if sart else K).append(ad)
    print(f"   {'GECTI' if sart else 'KALDI':<6} {ad}" + (f"   {detay}" if detay else ""))

print("="*74); print("K24 — ILERI ve TERS CIKARIM"); print("="*74)
c = Cikarim()
for _ in range(5):
    c.gozle("beyaz0_yani", "turuncu8")        # ft09 kurali
for _ in range(5):
    c.gozle("gri2_yani", "mavi9")

s, g = c.ne_olur("beyaz0_yani")
kontrol("ILERI: kosul -> sonuc", s == "turuncu8" and g == 1.0, f"{s} g={g:.2f}")
kontrol("az gozlemli kosulda karar YOK", c.ne_olur("hic_gorulmedi")[0] is None)

geri = c.neden_olabilir("turuncu8")
kontrol("TERS: sonuc -> sebep  ('bu boyleyse o oyledir')",
        geri and geri[0][0] == "beyaz0_yani", f"{geri}")
kontrol("ters yonde de guven var", geri[0][1] == 1.0)
kontrol("iki kural birbirine karismiyor",
        c.neden_olabilir("mavi9")[0][0] == "gri2_yani")

c2 = Cikarim()
for _ in range(3): c2.gozle("A", "X")
for _ in range(3): c2.gozle("B", "X")
g2 = c2.neden_olabilir("X")
kontrol("ayni sonucun IKI sebebi listeleniyor", len(g2) == 2, f"{[x[0] for x in g2]}")
kontrol("her sebep 0.5 paylasiyor", abs(g2[0][1]-0.5) < 0.01)

print()
print("="*74); print("K25 — DEGILLEME ('bu varsa bu OLAMAZ')"); print("="*74)
c3 = Cikarim()
for _ in range(10):
    c3.gozle("duvar_var", "hareket_yok")
kontrol("gozlenen sonuc OLAMAZ degil", not c3.olamaz_mi("duvar_var", "hareket_yok"))
kontrol("HIC gorulmeyen sonuc OLAMAZ", c3.olamaz_mi("duvar_var", "hareket_var"),
        "<-- negatif kural, pozitif kadar bilgi")
c3.gozle("duvar_var", "hareket_var")
kontrol("1/11 orani hala olamaz sayilir (esik 0.05 ust)",
        not c3.olamaz_mi("duvar_var", "hareket_var", esik=0.05), "1/11=0.09")
kontrol("olanaksizlar listesi",
        c3.olanaksizlar("duvar_var", ["hareket_yok","hareket_var","ucmak"]) == ["ucmak"])
kontrol("az gozlemde degilleme yapilmaz", not Cikarim().olamaz_mi("X","Y"))

print()
print("="*74); print("K26 — AYRIK ve ZINCIR"); print("="*74)
c4 = Cikarim()
for _ in range(5): c4.gozle("tikla", "kayar")
for _ in range(4): c4.gozle("tikla", "doner")
tek, gv = c4.ne_olur("tikla")
kontrol("baskin sonuc yoksa tek kural VERMEZ", tek is None, f"guven={gv:.2f}")
ay = c4.ayrik("tikla")
kontrol("AYRIK kume veriyor ('ya bu ya bu')", set(ay) == {"kayar","doner"}, f"{ay}")

c5 = Cikarim()
for _ in range(3): c5.gozle("A", "B")
for _ in range(3): c5.gozle("B", "C")
for _ in range(3): c5.gozle("C", "D")
z = c5.zincir("A")
kontrol("ZINCIR: A->B->C->D", z == ["A","B","C","D"], f"{z}")
kontrol("A'dan D'ye ulasilabilir", c5.ulasilabilir("A","D"))
kontrol("A'dan Z'ye ulasilamaz", not c5.ulasilabilir("A","Z"))
c6 = Cikarim()
for _ in range(3): c6.gozle("A","B")
for _ in range(3): c6.gozle("B","A")
kontrol("dongu sonsuza gitmiyor", len(c6.zincir("A", derinlik=10)) <= 3,
        f"{c6.zincir('A', derinlik=10)}")
kontrol("ozet uretiliyor", c5.ozet()["kosul"] == 3)

print()
print("="*74); print(f"SONUC: {len(G)} gecti, {len(K)} kaldi")
for k in K: print("   -", k)
print("="*74)
sys.exit(1 if K else 0)
