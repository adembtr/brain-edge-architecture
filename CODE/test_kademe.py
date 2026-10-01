"""
test_kademe.py — KADEME KADEME test. Adem: "her adimi full olduktan sonra
bastan uca test etmek gerek."

Buraya kadarki testler UCTAN UCA idi (25 oyun) -> gurultulu, hangi parcanin
calistigi belli degil. Bu dosya her mekanizmayi TEK BASINA, sentetik ve
DETERMINISTIK olarak sinar. Gercek oyun yok, rastgelelik yok.

  K5  nesne token'i     -> ayirmasi gerekeni ayiriyor, ayirmamasi gerekeni birlestiriyor mu
  K6  cukur mekanigi    -> doguyor / giriliyor / birlesiyor / erken cikiyor mu
  K7  hipotez mesafesi  -> mesafe dogru yonde mi degisiyor
"""
import os, sys
AGI = os.environ.get("AGI_DIR", os.path.abspath(os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..", "..", "arc-agi3-agent")))
os.environ.setdefault("OPERATION_MODE", "offline")
os.environ.setdefault("ENVIRONMENTS_DIR", f"{AGI}/environment_files")
os.environ.setdefault("MPLBACKEND", "agg")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, f"{AGI}/denme"); sys.path.insert(0, f"{AGI}/denme/infra")
import perception as P
from nesne import token, iliskiler, nesneler, _kova
from cukur import Cukur, Kase
import hedef as H

GECTI = []
KALDI = []


def kontrol(ad, sart, detay=""):
    (GECTI if sart else KALDI).append(ad)
    print(f"   {'GECTI' if sart else 'KALDI':<6} {ad}" + (f"   {detay}" if detay else ""))


def grid(satirlar):
    return tuple(tuple(int(c) for c in s) for s in satirlar)


# =====================================================================
print("=" * 74)
print("K5 — NESNE TOKEN'I")
print("=" * 74)

# ayni sekil, ayni renk, FARKLI KONUM -> AYNI token olmali (konum token'da yok)
g1 = grid(["00000000", "03300000", "03300000", "00000000",
           "00000330", "00000330", "00000000", "00000000"])
obs = nesneler(g1)
tk = [token(o, 8, 8) for o in obs]
kontrol("ayni sekil+renk, farkli konum -> AYNI token",
        len(obs) == 2 and tk[0] == tk[1], f"{len(obs)} nesne")

# ayni sekil, FARKLI RENK -> FARKLI token
g2 = grid(["00000000", "03300000", "03300000", "00000000",
           "00000550", "00000550", "00000000", "00000000"])
obs2 = nesneler(g2)
tk2 = [token(o, 8, 8) for o in obs2]
kontrol("ayni sekil, farkli renk -> FARKLI token",
        len(obs2) == 2 and tk2[0] != tk2[1])

# kare vs dikdortgen -> FARKLI token (genislik/uzunluk alanlari)
g3 = grid(["00000000", "03300000", "03300000", "00000000",
           "00003333", "00000000", "00000000", "00000000"])
obs3 = nesneler(g3)
tk3 = sorted([token(o, 8, 8) for o in obs3])
kontrol("kare vs cizgi -> FARKLI token", len(obs3) == 2 and tk3[0] != tk3[1])

# ILISKI atomlari
g4 = grid(["00000000", "03330000", "03530000", "03330000",
           "00000000", "05500000", "00000000", "00000000"])
obs4 = nesneler(g4)
ic, dg, es = iliskiler(obs4)
kontrol("iliski atomlari uretiliyor",
        len(ic) == len(obs4) and any(dg), f"icinde={sum(ic)} degiyor={sum(dg)}")

# esi_var: iki ayni sekil -> ikisinde de es=1
ic1, dg1, es1 = iliskiler(nesneler(g1))
kontrol("esi_var: ayni sekilden 2 tane -> ikisi de isaretli", all(es1))

# =====================================================================
print()
print("=" * 74)
print("K6 — CUKUR MEKANIGI")
print("=" * 74)
kase = Kase()
A = ("tokA", 3); B = ("tokB", 1)

c1 = kase.dogur({A}, [A, A], 10.0, tik=1)
kontrol("degisim ureten dizi -> CUKUR DOGAR", c1 is not None and kase.dogum == 1)

c0 = kase.dogur({A}, [A], 0.0, tik=1)
kontrol("degisim URETMEYEN dizi -> cukur DOGMAZ", c0 is None)

kontrol("giris = GOVDENIN kullandigi tokenlar (butun sahne DEGIL)",
        c1.giris == frozenset({"tokA"}), f"giris={set(c1.giris)}")

kontrol("giris saglanirsa uygun", c1.uygun(frozenset({"tokA", "tokB"})))
kontrol("giris saglanmazsa uygun DEGIL", not c1.uygun(frozenset({"tokB"})))

# verim: uzunluk bedava degil
kisa = Cukur({A}, [A], 10.0)
uzun = Cukur({A}, [A, A, A, A], 10.0)
kontrol("verim = degisim/uzunluk (uzun cukur cezali)",
        kisa.verim() > uzun.verim(), f"{kisa.verim():.1f} > {uzun.verim():.1f}")

# birlesme kanit ister
kase2 = Kase()
a = kase2.dogur({A}, [A, A], 10.0, 1)
b = kase2.dogur({B}, [B], 6.0, 1)
kontrol("kanitsiz birlesme YOK (a.uses=0)", kase2.birlestir(a, b, 2) is None)
a.harca(); a.ogren(10.0)
m = kase2.birlestir(a, b, 3)
kontrol("kanitli birlesme OLUR", m is not None and len(m.govde) == 3)
kontrol("birlesik cukurun gövdesi = a+b", m and m.govde == [A, A, B])

# verim dusuren birlesme reddedilir
kase3 = Kase()
x = kase3.dogur({A}, [A], 20.0, 1); x.harca(); x.ogren(20.0)
y = kase3.dogur({B}, [B, B, B, B, B], 1.0, 1)
kontrol("verimi dusuren birlesme REDDEDILIR", kase3.birlestir(x, y, 2) is None)

# N fizigi
c1.N = c1.Nmax
c1.harca()
kontrol("N kullanimda azalir", c1.N == c1.Nmax - 1)
for _ in range(20):
    c1.tik()
kontrol("N zamanla dolar", abs(c1.N - c1.Nmax) < 0.01)

# olum
z = Cukur({A}, [A], 5.0); z.q = 0.0; z.uses = 5
kontrol("q dusunce olur", z.olu())

# budama tavani
kase4 = Kase()
for i in range(80):
    kase4.dogur({(f"t{i}", 1)}, [(f"t{i}", 1)], float(i + 1), 1)
kase4.buda(ust=50)
kontrol("budama tavani calisiyor", len(kase4.cukurlar) <= 50,
        f"{len(kase4.cukurlar)} cukur")

# =====================================================================
print()
print("=" * 74)
print("K7 — HIPOTEZ MESAFESI")
print("=" * 74)
uzak = grid(["00000000", "03300000", "03300000", "00000000",
             "00000000", "00000330", "00000330", "00000000"])
yakin = grid(["00000000", "03303300", "03303300", "00000000",
              "00000000", "00000000", "00000000", "00000000"])
o_uzak, o_yakin = nesneler(uzak), nesneler(yakin)
tk = token(o_uzak[0], 8, 8)
ad, f = H.h_birlestir(tk)
m_uzak, m_yakin = f(o_uzak), f(o_yakin)
kontrol("birlestir: nesneler yakinlasinca mesafe AZALIR",
        m_yakin is not None and m_uzak is not None and m_yakin < m_uzak,
        f"{m_uzak:.0f} -> {m_yakin:.0f}")

ad2, f2 = H.h_temizle(tk)
bos = grid(["0" * 8] * 8)
kontrol("temizle: nesne kalmayinca mesafe TANIMSIZ (hipotez biter)",
        f2(nesneler(bos)) is None)
kontrol("temizle: 2 nesne varken mesafe = 2", f2(o_uzak) == 2.0)

hiza_bozuk = grid(["00000000", "03300000", "03300000", "00000000",
                   "00000000", "00000330", "00000330", "00000000"])
hiza_iyi = grid(["00000000", "03300330", "03300330", "00000000",
                 "00000000", "00000000", "00000000", "00000000"])
ad3, f3 = H.h_hizala(tk)
mb, mi = f3(nesneler(hiza_bozuk)), f3(nesneler(hiza_iyi))
kontrol("hizala: ayni satira gelince mesafe AZALIR",
        mb is not None and mi is not None and mi < mb, f"{mb:.0f} -> {mi:.0f}")

Hs = H.hipotez_uret(uzak)
kontrol("ilk kareden hipotez uretiliyor (EYLEM YAPMADAN)", len(Hs) > 0,
        f"{len(Hs)} hipotez: {sorted({h[0].split('_')[0] for h in Hs})}")
kontrol("hipotez isimleri CAKISMIYOR", len({h[0] for h in Hs}) == len(Hs))

# =====================================================================
print()
print("=" * 74)
print(f"SONUC: {len(GECTI)} gecti, {len(KALDI)} kaldi")
if KALDI:
    print("KALANLAR:")
    for k in KALDI:
        print("   -", k)
print("=" * 74)
sys.exit(1 if KALDI else 0)
