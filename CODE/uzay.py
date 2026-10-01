"""
uzay.py — Adres uzayi, nokta, bisimulation tiplemesi.

kenar_mimarisi.md §1'in nesneleri:
    Nokta  = durum. Frame'in geometrik/sayisal kodu. ETIKET YOK.
    Kenar  = o noktadaki ok.
    Noron  = ayni hedefi tahmin eden kenarlarin toplayicisi.
    Kase   = tum kenarlarin birlikte tanimladigi akis alani.

DEVIR.md 5.6 KOD KARARI (tek satir, her seyi acar):
    "adres uzayini (x,y) diye SABITLEME, BOYUT LISTESI olarak tut.
     Bugun [x,y], yarin [x,y,t], sonra [bant]. Kod ayni kalir."
Burada uygulandi: EKSENLER bir liste. t eklemek bir satir.

DEVIR.md 5.5: phi'nin tanim kumesi HAM DEGER degil, BISIMULATION TIPI.
    "Ayirt edilemez olanlari birlestirdigi icin kenar sayisini minimumda
     tutar. Ve ETIKETSIZ NESNE KIMLIGI uretir -- 'duvar' demeden duvari
     bulur."

DEVIR.md 11 (prior): No Free Lunch bir tasarim ilkesi. Yapisal prior'lar
(MDL, komsuluk, bisimulation) kacinilmaz ve dunya-bilgisi prior'larina
TERCIH EDILIR. Bu dosyadaki her sey yapisal prior'dur; hicbiri
"duvar/kutu/hedef" gibi dunya bilgisi tasimaz.
"""

import dunya


# =====================================================================
# 1. ADRES UZAYI — boyut listesi (sabit degil)
# =====================================================================
EKSENLER = ["x", "y"]          # yarin: ["x", "y", "t"]


def nokta(s, ekstra=None):
    """Durumun adres uzayindaki koordinati. Eksen listesi buyurse burasi
    otomatik buyur -- cagiran kod degismez."""
    d = {"x": s.ax, "y": s.ay}
    if ekstra:
        d.update(ekstra)
    return tuple(d[e] for e in EKSENLER)


def komsuluk_boyu(yaricap=1):
    """Yaricap-r komsulukta kac hucre var. DEVIR 5.6'nin uyarisi:
    2B'de 8, 3B'de 26. Bos eksen en pahali sey."""
    return (2 * yaricap + 1) ** len(EKSENLER) - 1


# =====================================================================
# 2. BISIMULATION TIPLEMESI
# =====================================================================
class BisimTipleyici:
    """
    Iki deger, TUM eylemler altinda ayirt edilemez etki uretiyorsa AYNI TIP.
        s1 ~ s2  <=>  for all a: a(s1) ~ a(s2)
    Partition refinement'in 1-adimlik hali (davranissal imza).

    ONEMLI: hicbir yerde "duvar" veya "kutu" gecmiyor. Tipler T0, T1, T2
    diye CIKIYOR. Isim yok, sadece ayirt edilemezlik.
    """

    def __init__(self):
        self.imza = {}       # ham deger -> {(eylem, etki), ...}
        self._tip = None

    def gozle(self, hedef_deger, eylem, etki):
        """etki = ajanin yer degisimi gibi gozlenebilir bir sonuc."""
        self.imza.setdefault(hedef_deger, set()).add((eylem, etki))
        self._tip = None

    def tipler(self):
        """ham deger -> tip id.  Ayni imzali degerler AYNI tipe duser."""
        if self._tip is None:
            grup, self._tip = {}, {}
            for v in sorted(self.imza):
                anahtar = frozenset(self.imza[v])
                if anahtar not in grup:
                    grup[anahtar] = len(grup)
                self._tip[v] = grup[anahtar]
        return self._tip

    def imza_parcalari(self, v):
        """
        Adem'in itirazi: "her nesneye bir sayi mi verdin? halbuki noronlarda
        bircok parcanin birlesmesi ile nesne olusur, bazen AYNI PARCALAR
        FARKLI NESNELERDE kullanilir."

        Hakli. Tip id (tek sayi) bilginin sikistirilmis halidir; parca
        kumesi ham halidir. Bir deger artik TEK TIP degil, PARCA KUMESI.
        Iki farkli nesne bazi parcalari PAYLASABILIR, hepsini degil.

        tip_of()  -> localist  (bir nesne = bir sayi)
        parcalar()-> dagitik   (bir nesne = parca kumesi)   <- LLM vektorune yakin
        """
        return frozenset(self.imza.get(v, ()))

    def parca_matrisi(self):
        """Hangi parca hangi degerlerde geciyor -> paylasim goruntusu."""
        tum = sorted({p for v in self.imza for p in self.imza[v]})
        return tum, {v: [1 if p in self.imza[v] else 0 for p in tum]
                     for v in sorted(self.imza)}

    def tip_sayisi(self):
        return len(set(self.tipler().values()))

    def tip_of(self, v):
        return self.tipler().get(v, -1)

    def rapor(self):
        t = self.tipler()
        ters = {}
        for v, ti in sorted(t.items()):
            ters.setdefault(ti, []).append(v)
        return {f"T{ti}": vs for ti, vs in sorted(ters.items())}


def tipleyici_ogren(kur_fn, adim_sayisi=1500, tohum=0):
    """Ajan rastgele gezerken tipleri KENDI kesfeder. Etiket verilmez."""
    import random
    rnd = random.Random(tohum)
    tp = BisimTipleyici()
    s = kur_fn()
    for t in range(adim_sayisi):
        if t % 120 == 0:
            s = kur_fn()
        a = rnd.choice(dunya.EYLEMLER)
        dx, dy = dunya.DELTA[a]
        hv = dunya.deger(s, s.ax + dx, s.ay + dy)
        s2 = dunya.adim(s, a)
        etki = dunya.yer_degisimi(s, s2)
        # eylemden bagimsiz imza: etki YONE gore normalize edilir
        norm = (0, 0) if etki == (0, 0) else (1, 0)
        tp.gozle(hv, "hareket", norm)
        tp.gozle(hv, "sayac", s2.sayac - s.sayac)
        s = s2
    return tp
