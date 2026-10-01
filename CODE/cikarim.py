"""
cikarim.py — CIFT YONLU CIKARIM. "O oyleyse bu, BU OYLEYSE O."

Adem: "o oyleyse bu boyledir, bu boyleyse o oyledir -- bu gibi baglamlari
bizim yapimiz uretmiyor mu?"

URETIYOR: kenarin kendisi zaten bir "eger-ise":  phi -> psi
  + dogum phi'yi daraltiyor  ("bu VE bu varsa")
  + bilesim atomu zincirliyor ("X sunu diyorsa")
  + nedensel baglam          ("A'ya dokununca B degisir")

URETMIYOR (bu dosya onlari ekler):
  1. TERS CIKARIM  psi -> phi   "su etkiyi gordum, sebebi ne olabilir?"
  2. DEGILLEME     "bu varsa bu OLAMAZ"
  3. AYRIK         "bu YA DA bu"
  4. ZINCIR        A->B ve B->C  =>  A->C

Adem'in ft09 notu tam cift yonlu bir kural:
    "beyaz 0'in oldugu taraf turuncu 8 olacak,
     gri 2'nin oldugu taraf mavi 9 olacak"
Tek yonlu kenarla bunun yarisi ogrenilir.
"""
from collections import defaultdict, Counter


class Cikarim:
    """Iki yonlu kural deposu. Kural = (kosul, sonuc)."""

    def __init__(self, en_az=2, esik=0.6):
        self.ileri = defaultdict(Counter)     # kosul -> sonuc sayaci
        self.geri = defaultdict(Counter)      # sonuc -> kosul sayaci   <-- TERS
        self.kosul_n = Counter()
        self.sonuc_n = Counter()
        self.en_az, self.esik = en_az, esik

    # ---------- gozlem ----------
    def gozle(self, kosul, sonuc):
        self.ileri[kosul][sonuc] += 1
        self.geri[sonuc][kosul] += 1          # AYNI ANDA ters yon
        self.kosul_n[kosul] += 1
        self.sonuc_n[sonuc] += 1

    # ---------- 1. ILERI: kosul -> sonuc ----------
    def ne_olur(self, kosul):
        n = self.kosul_n.get(kosul, 0)
        if n < self.en_az:
            return None, 0.0
        s, c = self.ileri[kosul].most_common(1)[0]
        return (s, c / n) if c / n >= self.esik else (None, c / n)

    # ---------- 2. TERS: sonuc -> kosul (abduction) ----------
    def neden_olabilir(self, sonuc, n_aday=3):
        """
        "Su etkiyi gordum, SEBEBI ne olabilir?"
        Planlamanin temeli: istedigim sonuca hangi kosul goturur.
        """
        n = self.sonuc_n.get(sonuc, 0)
        if n < self.en_az:
            return []
        return [(k, c / n) for k, c in self.geri[sonuc].most_common(n_aday)]

    # ---------- 3. DEGILLEME ----------
    def olamaz_mi(self, kosul, sonuc, esik=0.05):
        """
        "Bu varsa bu OLAMAZ." Kosul gorulduyse ama sonuc HIC/nadiren
        gelmediyse, bu bir NEGATIF kural. Pozitif kurallar kadar bilgi tasir.
        """
        n = self.kosul_n.get(kosul, 0)
        if n < self.en_az:
            return False
        return (self.ileri[kosul][sonuc] / n) <= esik

    def olanaksizlar(self, kosul, tum_sonuclar, esik=0.05):
        return [s for s in tum_sonuclar if self.olamaz_mi(kosul, s, esik)]

    # ---------- 4. AYRIK: "su ya da bu" ----------
    def ayrik(self, kosul, kapsama=0.9):
        """
        Tek bir sonuc baskin degilse, sonuclarin AYRIK kumesi dondurulur:
        "bu kosulda ya A ya B olur" -- tek kural yerine sinirli belirsizlik.
        """
        n = self.kosul_n.get(kosul, 0)
        if n < self.en_az:
            return []
        out, top = [], 0
        for s, c in self.ileri[kosul].most_common():
            out.append(s); top += c
            if top / n >= kapsama:
                break
        return out

    # ---------- 5. ZINCIR: A->B, B->C  =>  A->C ----------
    def zincir(self, kosul, derinlik=3):
        """Ileri kuralları zincirleyerek uzak sonucu cikar."""
        yol = [kosul]
        cur = kosul
        for _ in range(derinlik):
            s, g = self.ne_olur(cur)
            if s is None or s in yol:
                break
            yol.append(s); cur = s
        return yol

    def ulasilabilir(self, kosul, hedef, derinlik=4):
        """Bu kosuldan hedefe zincirle ulasilabiliyor mu?"""
        return hedef in self.zincir(kosul, derinlik)

    # ---------- ozet ----------
    def ozet(self):
        return dict(kosul=len(self.kosul_n), sonuc=len(self.sonuc_n),
                    ileri=sum(len(v) for v in self.ileri.values()),
                    geri=sum(len(v) for v in self.geri.values()))
