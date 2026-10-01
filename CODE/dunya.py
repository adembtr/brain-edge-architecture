"""
dunya.py — Olcum tezgahi. Kucuk, ayrik, ARC-benzeri dunya.

ARC-AGI-3 kisitlarina sadik:
  - frame degerleri 0-15
  - eylem sayisi <= 7
  - kazanma kosulu ajana SOYLENMEZ
  - etiket yok: ajan sadece sayi gorur, "duvar"/"kutu" kelimesi ajanda gecmez

Bu GERCEK ARC degil. Amaci tek sey: mimarinin bir iddiasini
izole edip olcebilecegimiz en kucuk dunya olmak.
"""

from collections import namedtuple

# Frame degerleri (bunlar DUNYANIN bilgisi, ajanin degil)
BOS, DUVAR, AJAN, KUTU = 0, 1, 2, 3

# ES-ANLAMLI degerler: 4 tipatip BOS gibi, 5 tipatip DUVAR gibi davranir.
# Ajan bunu BILMEZ -- sadece "4" ve "5" diye iki yeni sayi gorur.
# Bisimulation tiplemesinin isi tam olarak bunu KESFETMEK.
BOS2, DUVAR2 = 4, 5

# TOPLA (6): ajanin uzerinden GECEBILDIGI ama sayaci ARTIRAN hucre.
# Parcalarini iki farkli nesneyle PAYLASIR:
#   ("hareket", gecer)  <- BOS ile ortak
#   ("sayac", +1)       <- KUTU ile ortak
# Hicbiriyle ayni TIP degil. Localist temsil bunu ifade edemez.
TOPLA = 6

GECILEBILIR = (BOS, BOS2, TOPLA)
ENGEL       = (DUVAR, DUVAR2)

# Eylemler: 0=yukari 1=asagi 2=sol 3=sag
DELTA = {0: (0, -1), 1: (0, +1), 2: (-1, 0), 3: (+1, 0)}
EYLEMLER = (0, 1, 2, 3)

Durum = namedtuple("Durum", "grid ax ay sayac")


HARITA = [
    "1111111",
    "1000001",
    "1011001",
    "1000001",
    "1003001",
    "1000001",
    "1111111",
]


def kur(ax=1, ay=1):
    grid = tuple(tuple(int(c) for c in satir) for satir in HARITA)
    return Durum(grid=grid, ax=ax, ay=ay, sayac=0)


def _icerde(grid, x, y):
    return 0 <= y < len(grid) and 0 <= x < len(grid[0])


def deger(s, x, y):
    """Frame'in (x,y) hucresindeki sayi. Disarisi DUVAR gibi davranir."""
    if not _icerde(s.grid, x, y):
        return DUVAR
    return s.grid[y][x]


def deger_kare(grid, x, y):
    """Ham kareden okuma. Disarisi DUVAR gibi."""
    if not _icerde(grid, x, y):
        return DUVAR
    return grid[y][x]


def adim(s, a):
    """Dunyanin gercek fizigi. Ajan bunu BILMEZ, ogrenmek zorunda."""
    dx, dy = DELTA[a]
    nx, ny = s.ax + dx, s.ay + dy
    hedef = deger(s, nx, ny)

    if hedef in ENGEL:
        return s                                    # hareket yok

    if hedef == KUTU:
        bx, by = nx + dx, ny + dy
        if deger(s, bx, by) not in GECILEBILIR:
            return s                                # kutu sikismis
        # kutu itilir, ajan ilerler, sayac artar
        g = [list(r) for r in s.grid]
        g[ny][nx] = BOS
        g[by][bx] = KUTU
        return Durum(tuple(tuple(r) for r in g), nx, ny, s.sayac + 1)

    if hedef == TOPLA:
        g = [list(r) for r in s.grid]
        g[ny][nx] = BOS
        return Durum(tuple(tuple(r) for r in g), nx, ny, s.sayac + 1)

    return Durum(s.grid, nx, ny, s.sayac)


def yer_degisimi(s, s2):
    """Hedef degisken: ajan bu tikte ne kadar yer degistirdi."""
    return (s2.ax - s.ax, s2.ay - s.ay)


# Psi'nin deger kumesi: 5 olasi yer degisimi
YER_DEGISIMLERI = ((0, 0), (0, -1), (0, +1), (-1, 0), (+1, 0))


# =====================================================================
# HARITA2 — ayni fizik, ama BOS icin iki sayi (0,4), DUVAR icin iki (1,5).
# Ham deger uzayi 4 -> 6 buyudu. GERCEK tip sayisi hala 3.
# Bisimulation tiplemesi bunu goruyor mu? -> test_uzay.py
# =====================================================================
HARITA2 = [
    "1511151",
    "1004001",
    "1051001",
    "1400041",
    "1003001",
    "1040001",
    "1115111",
]


def kur2(ax=1, ay=1):
    grid = tuple(tuple(int(c) for c in satir) for satir in HARITA2)
    return Durum(grid=grid, ax=ax, ay=ay, sayac=0)


# HARITA3 — parca paylasimini gorunur kilan harita (deger 6 eklendi)
HARITA3 = [
    "1511151",
    "1064001",
    "1051001",
    "1400641",
    "1003001",
    "1046001",
    "1115111",
]


def kur3(ax=1, ay=1):
    grid = tuple(tuple(int(c) for c in satir) for satir in HARITA3)
    return Durum(grid=grid, ax=ax, ay=ay, sayac=0)
