"""test_baglam.py — K20-K22: BAGLAM."""
import sys, os
AGI = os.environ.get("AGI_DIR", os.path.abspath(os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..", "..", "arc-agi3-agent")))
os.environ.setdefault("OPERATION_MODE", "offline")
os.environ.setdefault("ENVIRONMENTS_DIR", f"{AGI}/environment_files")
os.environ.setdefault("MPLBACKEND", "agg")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, f"{AGI}/denme"); sys.path.insert(0, f"{AGI}/denme/infra")
from baglam import (baglam_vek, baglamli_kimlik, komsular, _yon, _uzak,
                    NedenselBaglam, baglamli_kimlikler)
from vektor import benzerlik, token_vek
from nesne import nesneler, token

G, K = [], []
def kontrol(ad, sart, detay=""):
    (G if sart else K).append(ad)
    print(f"   {'GECTI' if sart else 'KALDI':<6} {ad}" + (f"   {detay}" if detay else ""))

A = (3, 1, 1, 2, 1, 0, "-", 0, 0, 1, 0)
B = (9, 4, 4, 5, 0, 2, "yatay", 1, 1, 0, 1)
C = (5, 2, 2, 3, 1, 0, "-", 0, 0, 0, 1)

print("="*74); print("K20 — GEOMETRIK BAGLAM"); print("="*74)
kontrol("yon sembolu: sag ile sol FARKLI", _yon(5,0) != _yon(-5,0),
        f"{_yon(5,0)} vs {_yon(-5,0)}")
kontrol("yon sembolu: ayni yon AYNI", _yon(5,0) == _yon(10,0))
kontrol("uzaklik kovalari sirali", _uzak(1) < _uzak(10) < _uzak(40))

# ayni nesne (A), IKI FARKLI cevre
cevre1 = [(B, "y0", 0), (C, "y4", 0)]        # sagda B, solda C
cevre2 = [(C, "y0", 0), (B, "y4", 0)]        # TERS: sagda C, solda B
cevre3 = [(B, "y0", 0), (C, "y4", 0)]        # cevre1 ile ayni
k1 = baglamli_kimlik(A, cevre1)
k2 = baglamli_kimlik(A, cevre2)
k3 = baglamli_kimlik(A, cevre3)
kontrol("ayni nesne + AYNI cevre -> AYNI kimlik", benzerlik(k1,k3) > 0.9999)
kontrol("ayni nesne + YON DEGISMIS cevre -> FARKLI kimlik",
        benzerlik(k1,k2) < 0.35, f"benz={benzerlik(k1,k2):.2f}  <-- token AYNI!")
kontrol("baglamsiz token bunu AYIRT EDEMEZDI",
        benzerlik(token_vek(A), token_vek(A)) > 0.9999, "(ikisi de sadece A)")

bos = baglamli_kimlik(A, [])
kontrol("cevresiz nesne -> yine de kimlik var", bos is not None)
kontrol("cevresiz vs cevreli -> farkli", benzerlik(bos, k1) < 0.35)

cevre_yakin = [(B, "y0", 0)]
cevre_uzak  = [(B, "y0", 3)]
kontrol("AYNI komsu, farkli UZAKLIK -> farkli baglam",
        benzerlik(baglamli_kimlik(A,cevre_yakin),
                  baglamli_kimlik(A,cevre_uzak)) < 0.35)

print()
print("="*74); print("K21 — GERCEK IZGARADA BAGLAM"); print("="*74)
def grid(s): return tuple(tuple(int(c) for c in r) for r in s)
# ayni 2x2 kare iki kez: biri 5'lerle cevrili, digeri yalniz
g = grid(["000000000000",
          "005550000000",
          "005330000000",
          "005330000000",
          "005550000000",
          "000000000000",
          "000000000330",
          "000000000330",
          "000000000000",
          "000000000000",
          "000000000000",
          "000000000000"])
obs = nesneler(g)
kim = baglamli_kimlikler(obs, lambda o: token(o, 12, 12))
uc = [(tk, v, kms) for (tk, v, kms) in kim if tk[0] == 3]
kontrol("iki adet 3-renkli nesne bulundu", len(uc) == 2, f"{len(uc)}")
if len(uc) == 2:
    kontrol("TOKENLARI AYNI (baglamsiz ayirt edilemez)", uc[0][0] == uc[1][0])
    b = benzerlik(uc[0][1], uc[1][1])
    kontrol("BAGLAMLI KIMLIKLERI FARKLI", b < 0.5,
            f"benz={b:.2f}  <-- biri cevrili, digeri yalniz")
    kontrol("cevrili olanin komsusu var", len(uc[0][2]) > 0 or len(uc[1][2]) > 0)

print()
print("="*74); print("K22 — NEDENSEL BAGLAM (eylemden ogrenilir)"); print("="*74)
nb = NedenselBaglam()
for _ in range(4):
    nb.gozle(A, [B])          # A'ya dokununca hep B degisiyor
for _ in range(4):
    nb.gozle(C, [])           # C'ye dokununca hicbir sey
kontrol("A -> B bagi guclu", nb.guc(A, B) == 1.0, f"{nb.guc(A,B):.2f}")
kontrol("A -> C bagi yok", nb.guc(A, C) == 0.0)
kontrol("etkiledikleri dogru", nb.etkiledikleri(A) == [B])
kontrol("C hicbir sey etkilemiyor", nb.etkiledikleri(C) == [])
kontrol("UZAKTAN bag tespit ediliyor (geometrik komsu degil)",
        nb.uzaktan_mi(A, B, kms=[(C, "y0", 0)]),
        "<-- kapi-anahtar / uzak sayac")
kontrol("geometrik komsuysa 'uzaktan' degil",
        not nb.uzaktan_mi(A, B, kms=[(B, "y0", 0)]))
nb2 = NedenselBaglam()
nb2.gozle(A, [B])
kontrol("tek gozlemle karar VERMIYOR (en_az=2)", nb2.etkiledikleri(A) == [])
kontrol("nedensel imza uretiliyor", nb.nedensel_vek(A) is not None)
kontrol("etkileyen ile etkilemeyen imza FARKLI",
        benzerlik(nb.nedensel_vek(A), nb.nedensel_vek(C)) < 0.35)

print()
print("="*74); print("K23 — BAGLAMLI KIMLIK ANAHTAR OLARAK"); print("="*74)
from kimlik import baglam_kodu, kimlik_vek
hepsi = [(A,(0.0,0.0)), (B,(5.0,0.0)), (C,(-5.0,0.0))]
k_orta = baglam_kodu(A,(0.0,0.0), hepsi)
hepsi2 = [(A,(0.0,0.0)), (C,(5.0,0.0)), (B,(-5.0,0.0))]      # B ve C YER DEGISTI
k_ters = baglam_kodu(A,(0.0,0.0), hepsi2)
kontrol("baglam kodu hashlenebilir", isinstance(k_orta, tuple) and hash(k_orta) is not None)
kontrol("komsular yer degistirince KOD degisir", k_orta != k_ters, f"{len(k_orta)} komsu")
kontrol("ayni sahne -> ayni kod", k_orta == baglam_kodu(A,(0.0,0.0), hepsi))
v1 = kimlik_vek((A, k_orta)); v2 = kimlik_vek((A, k_ters))
kontrol("ayni token + farkli baglam -> FARKLI kimlik vektoru",
        benzerlik(v1, v2) < 0.5, f"benz={benzerlik(v1,v2):.2f}")
kontrol("ayni token + ayni baglam -> AYNI vektor",
        benzerlik(v1, kimlik_vek((A, k_orta))) > 0.9999)
kontrol("baglamsiz kimlik de uretilebiliyor", kimlik_vek((A, ())) is not None)
print()
print(f"K23 sonrasi: {len(G)} gecti, {len(K)} kaldi")


print()
print("="*74); print(f"SONUC: {len(G)} gecti, {len(K)} kaldi")
for k in K: print("   -", k)
print("="*74)
sys.exit(1 if K else 0)
