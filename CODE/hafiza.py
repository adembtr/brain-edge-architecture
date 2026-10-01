"""
hafiza.py — OYUNA OZEL, DISKTE KALICI HAFIZA + ISRAR.

Adem'in uc gozlemi:

1. ISRAR YOK: "bir eylem bir sey degistiriyorsa onu TEKRAR etmeli, ama
   bizimki saga gidip sola gidiyor, etrafinda donuyor. Halbuki INSAN
   EYLEMI SONA KADAR GOTURUR."
   -> Ajan her adimda skoru yeniden hesapliyordu ve salinip duruyordu.
      Artik: degisim ureten (token,eylem) TUKENENE KADAR tekrarlanir.

2. HAFIZA YOK: "hafiza.txt olmali, ne eylem yaptiysa yazmali. Isee yarayan
   eylemleri de FARKLI hafizaya almali. HER OYUN ICIN FARKLI hafiza."
   -> HAFIZA/<oyun>.txt            her eylem
      HAFIZA/<oyun>_ise_yarayan.txt  degisim ureten eylemler
      HAFIZA/<oyun>_recete.txt       seviye geciren dizi

3. SEVIYE RECETESI: "seviye gecince SON HALE bakmali, 'hee demek ki bu
   seviye geciriyor', diger seviyelerde AYNI SEYI yapmaya calismali."
   -> Seviye atlayan son K adim recete olarak saklanir; sonraki seviyede
      ONCE o denenir.

Hafiza diskte kalir: ikinci kosu birincinin bildigiyle baslar.
"""
import os, json
from collections import Counter


def _tupleize(x):
    """JSON listeleri geri tuple'a cevirir (IC ICE olanlar dahil).
    Anahtar artik (token, baglam_kodu) gibi ic ice -> hashlenebilir olmali."""
    if isinstance(x, (list, tuple)):
        return tuple(_tupleize(i) for i in x)
    return x

KLASOR = os.environ.get("BRAIN_HAFIZA", os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "HAFIZA"))


class Hafiza:
    def __init__(self, oyun, klasor=KLASOR, recete_uzunluk=8):
        self.oyun = oyun
        self.klasor = klasor
        self.recete_uzunluk = recete_uzunluk
        os.makedirs(klasor, exist_ok=True)
        self.tum = []             # (adim, token, eylem, degisim, seviye)
        self.ise_yarayan = []     # (token, eylem, ort_degisim, kac_kez)
        self._iy = {}             # (token,eylem) -> [toplam_degisim, adet]
        self.receteler = []       # [[(token,eylem), ...], ...]
        self.son_adimlar = []     # kayan pencere

    # ---------- yazma ----------
    def yaz(self, adim, tk, eylem, degisim, seviye):
        self.tum.append((adim, tk, eylem, degisim, seviye))
        self.son_adimlar.append((tk, eylem))
        if len(self.son_adimlar) > self.recete_uzunluk:
            self.son_adimlar.pop(0)
        if degisim > 0:
            a = self._iy.setdefault((tk, eylem), [0.0, 0])
            a[0] += degisim; a[1] += 1

    def seviye_atladi(self):
        """SON HALE BAK: seviyeyi geciren son adimlar = RECETE."""
        if self.son_adimlar:
            self.receteler.append(list(self.son_adimlar))
            self.son_adimlar = []
        return self.receteler[-1] if self.receteler else []

    # ---------- okuma ----------
    def ise_yarar_mi(self, tk, eylem):
        a = self._iy.get((tk, eylem))
        return (a[0] / a[1]) if a else 0.0

    def en_iyiler(self, n=10):
        return sorted(((v[0]/v[1], v[1], k) for k, v in self._iy.items()),
                      reverse=True)[:n]

    def recete_adimlari(self):
        """Butun receteleri tek listede (sonraki seviyede denenecek)."""
        out = []
        for r in self.receteler:
            out.extend(r)
        return out

    # ---------- disk ----------
    def kaydet(self):
        with open(f"{self.klasor}/{self.oyun}.txt", "w") as f:
            f.write("# adim | token | eylem | degisim | seviye\n")
            for (a, tk, e, d, s) in self.tum:
                f.write(f"{a}\t{tk}\t{e}\t{d:.0f}\t{s}\n")
        with open(f"{self.klasor}/{self.oyun}_ise_yarayan.txt", "w") as f:
            f.write("# ort_degisim | kac_kez | token | eylem\n")
            for (ort, adet, (tk, e)) in sorted(
                    ((v[0]/v[1], v[1], k) for k, v in self._iy.items()),
                    reverse=True):
                f.write(f"{ort:.1f}\t{adet}\t{tk}\t{e}\n")
        with open(f"{self.klasor}/{self.oyun}_recete.txt", "w") as f:
            f.write("# seviye geciren diziler (son hale goturen adimlar)\n")
            for i, r in enumerate(self.receteler):
                f.write(f"--- recete {i+1} (seviye {i+1}) ---\n")
                for (tk, e) in r:
                    f.write(f"  eylem {e}  token {tk}\n")
        json.dump({"iy": [[k[0], k[1], v[0], v[1]] for k, v in self._iy.items()],
                   "receteler": [[[tk, e] for (tk, e) in r]
                                 for r in self.receteler]},
                  open(f"{self.klasor}/{self.oyun}.json", "w"))

    def yukle(self):
        """Onceki kosunun bildigiyle basla."""
        yol = f"{self.klasor}/{self.oyun}.json"
        if not os.path.exists(yol):
            return False
        d = json.load(open(yol))
        for (tk, e, tot, adet) in d.get("iy", []):
            self._iy[(_tupleize(tk), e)] = [tot, adet]
        for r in d.get("receteler", []):
            self.receteler.append([(_tupleize(tk), e) for (tk, e) in r])
        return True


class Israrci:
    """
    "Insan eylemi sona kadar goturur."
    Degisim ureten (token,eylem) TUKENENE KADAR tekrarlanir.
    Tukenme = ust uste `sabir` kez degisim uretmemesi.
    """

    def __init__(self, sabir=2, ust_sinir=8):
        self.aktif = None
        self.bos_sayac = 0
        self.tekrar = 0
        self.sabir = sabir
        self.ust_sinir = ust_sinir

    def onerir(self, adaylar):
        """Israr edilecek (token,eylem) varsa dondur, yoksa None."""
        if self.aktif is None:
            return None
        if self.aktif not in adaylar:          # nesne sahneden kalkti
            self.birak()
            return None
        return self.aktif

    def bildir(self, k, degisim, yararli=None):
        """
        OLCULEN HATA: israr "degisim > 0" ile tetikleniyordu. Ama bu
        oyunlarda neredeyse HER eylem bir seyi degistiriyor (vc33: her
        tiklama kareyi degistiriyor). Sonuc: 800 adimin 520-776'si israr,
        ajan takildi, seviyeler DUSTU (bp35, ft09 kayboldu).

        Dogrusu: israr degisim OLDUGU icin degil, ISE YARADIGI icin.
        yararli=True  -> hipotezin mesafesini azaltti (asil sinyal)
        yararli=None  -> geriye donus: degisim buyuklugune bak
        """
        if yararli is None:
            yararli = degisim > 0
        if yararli:
            if self.aktif == k:
                self.tekrar += 1
                self.bos_sayac = 0
                if self.tekrar >= self.ust_sinir:
                    self.birak()
            else:
                self.aktif = k; self.tekrar = 1; self.bos_sayac = 0
        else:
            if self.aktif == k:
                self.bos_sayac += 1
                if self.bos_sayac >= self.sabir:
                    self.birak()               # TUKENDI, sira baskasina

    def birak(self):
        self.aktif = None; self.bos_sayac = 0; self.tekrar = 0
