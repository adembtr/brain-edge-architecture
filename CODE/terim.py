"""
terim.py — phi ve psi'yi VERI yapar. Python lambda'si DEGIL.

NEDEN (Adem'in sorusu: "LLM'de .pt var, bizde ne var?"):

    LLM'in agirligi SAYI     -> tensor -> .pt dosyasi
    Bizim agirligimiz KURAL  -> terim  -> .kase dosyasi

Lambda kaydedilemez, karsilastirilamaz, uretilemez, mutasyona ugratilamaz.
Terim (veri) hepsini yapabilir. Bu tek degisiklik dort kapiyi birden acar:

    1. KAYIT    -> beyin diske yazilabilir  (.kase)
    2. DOGUM    -> yeni terim URETILEBILIR  (lambda uretilemez)
    3. BUDAMA   -> terimler karsilastirilir, ayni olan birlestirilir
    4. BILESIM  -> bir noronun ciktisi bir ATOM olur -> yeni kelime

AYRICA — Adem'in "nokta neden tek sayi, vektor olamaz mi?" itirazi:
    Hakli. Artik bir hucre TEK TIP degil, PARCA KUMESI.
    Parcalar nesneler ARASINDA PAYLASILIR (bkz. imza_parcalari).
"""

import json


def _dondur(x):
    """JSON listeyi geri tuple yapar. Ic ice olanlar dahil (hashlenebilirlik)."""
    if isinstance(x, (list, tuple)):
        return tuple(_dondur(i) for i in x)
    return x


# =====================================================================
# BAGLAM — atomlarin degerlendirilmesi icin gereken dis bilgi
# =====================================================================
class Baglam:
    """Terimler saf veridir; onlari OKUMAK icin baglam gerekir."""

    def __init__(self, dunya=None, tipleyici=None):
        self.dunya = dunya
        self.tipleyici = tipleyici
        self.noronlar = {}          # ad -> Neuron   (BILESIM icin)

    # -- dunya erisimi --------------------------------------------------
    def hedef_deger(self, s, a):
        dx, dy = self.dunya.DELTA[a]
        return self.dunya.deger(s, s.ax + dx, s.ay + dy)

    def otesi_deger(self, s, a):
        dx, dy = self.dunya.DELTA[a]
        return self.dunya.deger(s, s.ax + 2 * dx, s.ay + 2 * dy)

    def tip(self, v):
        return self.tipleyici.tip_of(v) if self.tipleyici else v

    def iz_deger(self, iz, dx, dy, dt):
        """(x, y, t) ADRES UZAYINDA okuma.

        DEVIR.md 5.6: "ucuncu eksen ZAMAN. (x,y,t)'de hareket YEREL bir
        ozellik olur -- egik cizgi. Hafiza gerekmez. Hiz = egim."

        dt=0 -> su anki kare, dt=1 -> bir onceki, ...
        odak noktasi (x,y) baslangici: sahnedeki hareketli nesnenin yeri.
        """
        # ONEMLI (olculmus hata): ORIJIN SU ANKI odakta SABIT kalmali.
        # Orijini de gecmise kaydirirsak nesne kendi gecmisinde hep (0,0)'da
        # durur ve HIZ GORUNMEZ olur -- tam da gormek istedigimiz sey.
        # (x,y,t)'de hareketin yerel olmasi, uzaysal orijinin SABIT
        # olmasina bagli. Zaman ekseni kareyi degistirir, orijini degil.
        kare = iz.kare(dt)
        if kare is None:
            return -1
        ox, oy = iz.odak(0)
        if ox is None:
            return -1
        return self.dunya.deger_kare(kare, ox + dx, oy + dy)

    def parcalar(self, v):
        """Bir degerin DAVRANIS PARCALARI. Paylasilabilir."""
        return self.tipleyici.imza_parcalari(v) if self.tipleyici else frozenset()


BAGLAM = Baglam()


# =====================================================================
# ATOMLAR — phi'nin alfabesi. Her atom saf veri: (ad, *argumanlar)
# =====================================================================
def _at_eylem(s, a, k):
    return a == k

def _at_hedef_tip(s, a, k):
    return BAGLAM.tip(BAGLAM.hedef_deger(s, a)) == k

def _at_otesi_tip(s, a, k):
    return BAGLAM.tip(BAGLAM.otesi_deger(s, a)) == k

def _at_hedef_parca(s, a, *p):
    """PAYLASILAN PARCA. Iki farkli nesne ayni parcayi tasiyabilir."""
    return tuple(p) in BAGLAM.parcalar(BAGLAM.hedef_deger(s, a))

def _at_otesi_parca(s, a, *p):
    return tuple(p) in BAGLAM.parcalar(BAGLAM.otesi_deger(s, a))

_NORON_YIGINI = set()          # dongu koruyucusu (ikinci savunma hatti)


def _at_noron(s, a, ad, *deger):
    """*** BILESIM ***  Baska bir noronun ciktisi BURADA bir yuklem olur.
    Sistemin KENDI URETTIGI kelime budur."""
    n = BAGLAM.noronlar.get(ad)
    if n is None or ad in _NORON_YIGINI:
        return False
    _NORON_YIGINI.add(ad)
    try:
        t, _, _ = n.predict(s, a)
    finally:
        _NORON_YIGINI.discard(ad)
    return t == (deger[0] if len(deger) == 1 else tuple(deger))


def _at_konum(s, a, x):
    """MUTLAK konum. (x,y) uzayinda ezberlemeye izin verir -- t'siz
    cozumun mumkun olmasi icin gerekli, boylece SIKISTIRMA olculebilir."""
    ox, oy = s.odak(0)
    return ox == x


def _at_konum_y(s, a, y):
    ox, oy = s.odak(0)
    return oy == y


def _at_nokta(s, a, dx, dy, dt, deger):
    """(dx, dy, dt) adresindeki hucre `deger` mi? -- tek atom, uc eksen."""
    return BAGLAM.iz_deger(s, dx, dy, dt) == deger


ATOM_TABLOSU = {
    "nokta":        _at_nokta,
    "konum":        _at_konum,
    "konum_y":      _at_konum_y,
    "eylem":        _at_eylem,
    "hedef_tip":    _at_hedef_tip,
    "otesi_tip":    _at_otesi_tip,
    "hedef_parca":  _at_hedef_parca,
    "otesi_parca":  _at_otesi_parca,
    "noron":        _at_noron,       # <- kendi uretti-gi kelime
}


def atom_degerlendir(atom, s, a):
    return ATOM_TABLOSU[atom[0]](s, a, *atom[1:])


# =====================================================================
# TERIM — atomlarin VE'si.  phi = terim.
# =====================================================================
class Terim:
    __slots__ = ("atomlar",)

    def __init__(self, atomlar=()):
        self.atomlar = tuple(sorted(set(_dondur(x) for x in atomlar), key=str))

    def __call__(self, s, a):
        for at in self.atomlar:
            if not atom_degerlendir(at, s, a):
                return False
        return True

    # MDL: kisa terim ucuzdur.
    def uzunluk(self):
        return len(self.atomlar)

    def daralt(self, atom):
        return Terim(self.atomlar + (tuple(atom),))

    def icerir(self, atom):
        return tuple(atom) in self.atomlar

    def json(self):
        return [list(a) for a in self.atomlar]

    @staticmethod
    def yukle(veri):
        return Terim(tuple(_dondur(a) for a in veri))

    def __eq__(self, o):
        return isinstance(o, Terim) and self.atomlar == o.atomlar

    def __hash__(self):
        return hash(self.atomlar)

    def __repr__(self):
        if not self.atomlar:
            return "her_zaman"
        return "&".join(a[0] + "=" + ",".join(map(str, a[1:])) for a in self.atomlar)


# =====================================================================
# TAHMIN (psi) — bu da veri.
# =====================================================================
class Tahmin:
    """DEGISIM tahmini.  Adem'in ilkesi (DEVIR 5.7): mutlak deger degil
    DEGISIM kodlanir. Bu yuzden psi bir 'sonraki nokta' degil bir DELTA."""

    __slots__ = ("delta",)

    def __init__(self, delta):
        self.delta = tuple(delta)

    def __call__(self, s, a):
        return self.delta

    # *** KAPALILIK ***  Delta'lar TOPLAMA ALTINDA KAPALI bir grup olusturur.
    # Yani "degisim" temsilinden vazgecmeden bilesim yapilabilir.
    def besteleI(self, o):
        return Tahmin(tuple(x + y for x, y in zip(self.delta, o.delta)))

    def json(self):
        return list(self.delta)

    @staticmethod
    def yukle(v):
        return Tahmin(tuple(v))

    def __eq__(self, o):
        return isinstance(o, Tahmin) and self.delta == o.delta

    def __hash__(self):
        return hash(self.delta)

    def __repr__(self):
        return f"D{self.delta}"
