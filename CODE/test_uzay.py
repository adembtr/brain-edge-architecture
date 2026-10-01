"""
test_uzay.py — Uzay + bisimulation + prior olcumleri, ve N5/N6'nin duzeltilmis hali.
"""
import random, math
import dunya, uzay
from neuron import Neuron, EdgeP, KURALLAR

KURAL = "ozel_isabet"      # test_neuron.py TEST N3'un olculmus kazanani


# ---------------------------------------------------------------- havuzlar
def _yuklemler(tipleyici=None):
    """tipleyici=None -> HAM DEGER yuklemleri.  verilirse -> BISIM TIPI."""
    y = [(f"eylem={k}", (lambda k: lambda s, a: a == k)(k)) for k in dunya.EYLEMLER]

    def hd(s, a):
        dx, dy = dunya.DELTA[a]; return dunya.deger(s, s.ax + dx, s.ay + dy)

    def od(s, a):
        dx, dy = dunya.DELTA[a]; return dunya.deger(s, s.ax + 2*dx, s.ay + 2*dy)

    if tipleyici is None:
        degerler = sorted({v for r in dunya.kur2().grid for v in r})
        for v in degerler:
            y.append((f"hedef_deger={v}", (lambda v: lambda s,a: hd(s,a)==v)(v)))
            y.append((f"otesi_deger={v}", (lambda v: lambda s,a: od(s,a)==v)(v)))
    else:
        T = tipleyici
        for ti in range(T.tip_sayisi()):
            y.append((f"hedef_tip=T{ti}", (lambda ti: lambda s,a: T.tip_of(hd(s,a))==ti)(ti)))
            y.append((f"otesi_tip=T{ti}", (lambda ti: lambda s,a: T.tip_of(od(s,a))==ti)(ti)))
    return y


def havuz(tipleyici=None, derinlik=2, psi_kumesi=None):
    yuk = _yuklemler(tipleyici)
    psi_kumesi = psi_kumesi or dunya.YER_DEGISIMLERI
    phis = [("her_zaman", lambda s,a: True, 0)] + [(n,f,1) for n,f in yuk]
    if derinlik >= 2:
        for i in range(len(yuk)):
            for j in range(i+1, len(yuk)):
                (n1,f1),(n2,f2) = yuk[i], yuk[j]
                phis.append((f"{n1}&{n2}",
                    (lambda f1,f2: lambda s,a: f1(s,a) and f2(s,a))(f1,f2), 2))
    return [EdgeP(pf, (lambda d: lambda s,a: d)(d), f"{pn}->{d}", ozgulluk=oz)
            for (pn,pf,oz) in phis for d in psi_kumesi]


# ---------------------------------------------------------------- kosu
def kosu(noron, kur_fn, adim_sayisi=1600, tohum=0, bolum=150, pencere=400,
         adim_carpani=1, katmanla=False):
    rnd = random.Random(tohum)
    s = kur_fn()
    isabet, kutu = [], {}
    for t in range(adim_sayisi):
        if t % bolum == 0: s = kur_fn()
        a = rnd.choice(dunya.EYLEMLER)
        tahmin,_,_ = noron.predict(s, a)
        s2 = s
        for _ in range(adim_carpani): s2 = dunya.adim(s2, a)
        gercek = dunya.yer_degisimi(s, s2)
        ok = 1 if tahmin == gercek else 0
        isabet.append(ok)
        if katmanla:
            dx,dy = dunya.DELTA[a]
            hv = dunya.deger(s, s.ax+dx, s.ay+dy)
            ad = "KUTU-bitisik (nadir)" if hv == dunya.KUTU else "acik zemin (sik)"
            kutu.setdefault(ad, []).append(ok)
        noron.learn(s, a, gercek); noron.tick()
        if t % 50 == 49: noron.buda()
        s = dunya.adim(s, a)
    son = isabet[-pencere:]
    return sum(son)/len(son), len(noron.kenarlar), {k:(sum(v)/len(v), len(v)) for k,v in kutu.items()}


def yap(kenarlar, hedef="ajan_yer_degisimi"):
    n = Neuron(hedef, kurall=KURAL)
    for e in kenarlar: n.bagla(e)
    return n


# =====================================================================
print("="*76)
print("TEST U1 — BISIMULATION: etiketsiz nesne kimligi  (kenar_mimarisi §5.5)")
print("="*76)
for ad, fn in (("HARITA1", dunya.kur), ("HARITA2 (es-anlamli sayilar)", dunya.kur2)):
    T = uzay.tipleyici_ogren(fn)
    print(f"  {ad:30} ham deger={len(T.imza)} -> TIP={T.tip_sayisi()}  {T.rapor()}")
print("  >> 0 ve 4 ayni tipe, 1 ve 5 ayni tipe dustu. 'duvar' kelimesi GECMIYOR.")

T2 = uzay.tipleyici_ogren(dunya.kur2)

print()
print("="*76)
print("TEST U2 — PRIOR'IN BEDELI/KARI: ham deger phi vs bisim tipi phi")
print("Ayni dunya (HARITA2), ayni kural, ayni derinlik. Tek fark: phi'nin dili.")
print("="*76)
print(f"  {'phi dili':<22}{'yuklem':>8}{'kenar':>8}{'canli':>8}{'dogruluk':>11}")
for ad, tp in (("ham deger", None), ("bisim tipi", T2)):
    h = havuz(tp, derinlik=2)
    n = yap(h)
    d, k, _ = kosu(n, dunya.kur2)
    print(f"  {ad:<22}{len(_yuklemler(tp)):>8}{len(h):>8}{k:>8}{d:>11.3f}")
print("  >> Tipleme kenar sayisini dusurup dogrulugu korursa prior KARLI.")

print()
print("="*76)
print("TEST U3 — N6 DUZELTILMIS: gerekli yuklem yoksa ne olur? (KATMANLI olcum)")
print("Onceki N6 null cikti cunku kutu-bitisik durum NADIR; ortalama onu yutuyor.")
print("Simdi ayri olculuyor.")
print("="*76)
def eksik_havuz(tp, yasak_ek):
    yuk = [(n,f) for n,f in _yuklemler(tp) if not n.startswith(yasak_ek)]
    phis = [("her_zaman", lambda s,a: True, 0)] + [(n,f,1) for n,f in yuk]
    for i in range(len(yuk)):
        for j in range(i+1, len(yuk)):
            (n1,f1),(n2,f2) = yuk[i], yuk[j]
            phis.append((f"{n1}&{n2}", (lambda f1,f2: lambda s,a: f1(s,a) and f2(s,a))(f1,f2), 2))
    return [EdgeP(pf,(lambda d: lambda s,a:d)(d), f"{pn}->{d}", ozgulluk=oz)
            for (pn,pf,oz) in phis for d in dunya.YER_DEGISIMLERI]

print(f"  {'havuz':<34}{'genel':>9}{'acik zemin':>13}{'KUTU-bitisik':>15}")
for ad, h in (("TAM (otesi_tip var)",        havuz(T2, 2)),
              ("EKSIK (otesi_tip YOK)",      eksik_havuz(T2, "otesi_tip"))):
    n = yap(h)
    d, k, kat = kosu(n, dunya.kur2, katmanla=True)
    a1 = kat.get("acik zemin (sik)", (float('nan'),0))
    a2 = kat.get("KUTU-bitisik (nadir)", (float('nan'),0))
    print(f"  {ad:<34}{d:>9.3f}{a1[0]:>13.3f}{a2[0]:>15.3f}   (n={a2[1]})")
print("  >> Fark KUTU-bitisik sutununda gorunmeli. Genel ortalama yaniltici.")

print()
print("="*76)
print("TEST U4 — N5 DUZELTILMIS: 2 tik ilerisi, psi kumesi DOGRU verildi")
print("Onceki N5 hileliydi: 2-tik hedefinin degerleri havuzda hic yoktu.")
print("Simdi 9 degerin hepsi veriliyor -> temsil bahanesi kalmiyor.")
print("="*76)
PSI2 = ((0,0),(0,-1),(0,1),(-1,0),(1,0),(0,-2),(0,2),(-2,0),(2,0))
print(f"  {'hedef':<16}{'psi':>6}{'kenar':>8}{'dogruluk':>11}")
n1 = yap(havuz(T2, 2)); d1,k1,_ = kosu(n1, dunya.kur2)
print(f"  {'1 tik':<16}{len(dunya.YER_DEGISIMLERI):>6}{k1:>8}{d1:>11.3f}")
n2 = yap(havuz(T2, 2, psi_kumesi=PSI2), hedef="2tik")
d2,k2,_ = kosu(n2, dunya.kur2, adim_carpani=2)
print(f"  {'2 tik (duz)':<16}{len(PSI2):>6}{k2:>8}{d2:>11.3f}")
print(f"\n  duz kenarin 2-tikteki kaybi: {d1-d2:+.3f}")
print("  Bilesim olsaydi: 1-tik noronunu KENDI CIKTISI uzerine 2 kez uygula.")
print("  Duz cozum icin phi derinligi k ile ustel; bilesimde DOGRUSAL.")

print()
print("="*76); print("UZAY OLCUMLERI TAMAM"); print("="*76)
