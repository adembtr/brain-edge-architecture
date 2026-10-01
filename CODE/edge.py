"""
edge.py — Tek sinaps (kenar).

Kenar = kendi kullanim gecmisini tasiyan kucuk bir tahminci.
Minimal hali: (phi, psi, q, N). p ve g YOK — olculmus bir basarisizlik
talep etmeden eklenmeyecek.
"""


class Edge:
    __slots__ = ("phi", "psi", "q", "N", "Nmax", "alpha", "tau", "beta",
                 "name", "uses", "hits")

    def __init__(self, phi, psi, name="", q=0.5, Nmax=4.0,
                 alpha=0.30, tau=3.0, beta=1.0):
        self.phi = phi        # (s, a) -> bool     onkosul
        self.psi = psi        # (s, a) -> deger    tahmin
        self.q = q            # iddia gucu     [0,1]  yavas
        self.N = Nmax         # kullanim butcesi      hizli
        self.Nmax = Nmax
        self.alpha = alpha    # q ogrenme hizi
        self.tau = tau        # N dolum zaman sabiti
        self.beta = beta      # surpriz butce iadesi
        self.name = name
        self.uses = 0
        self.hits = 0

    # --- okuma ---------------------------------------------------------
    def active(self, s, a):
        return self.phi(s, a)

    def q_eff(self):
        """Etkin agirlik. N tukendiyse kenar susar (dogru olsa bile)."""
        return self.q * (self.N / self.Nmax)

    def predict(self, s, a):
        return self.psi(s, a)

    # --- yazma ---------------------------------------------------------
    def spend(self):
        """Sadece EYLEME GEREKCE olurken cagrilir. Tahmin bedava."""
        self.N = max(0.0, self.N - 1.0)
        self.uses += 1

    def tick(self):
        """Her adimda, kullanilsin kullanilmasin."""
        self.N += (self.Nmax - self.N) / self.tau

    def learn(self, err):
        """err in [0,1]. 0 = tam isabet."""
        self.q = _clip(self.q + self.alpha * (1.0 - 2.0 * err), 0.0, 1.0)
        # Surpriz bilgi getirdi -> butce iadesi. Verimli kullanim
        # cezalandirilmasin.
        self.N = min(self.Nmax, self.N + self.beta * err)
        if err < 0.5:
            self.hits += 1

    def dead(self, q_min=0.05):
        return self.q < q_min

    def specialize(self, extra_phi, name=""):
        """Hatayi en az bilgiyle acikla: phi'yi daralt, yeni kenar dogur."""
        old = self.phi
        return Edge(lambda s, a: old(s, a) and extra_phi(s, a),
                    self.psi, name or (self.name + "+"), q=self.q,
                    Nmax=self.Nmax, alpha=self.alpha, tau=self.tau,
                    beta=self.beta)

    def __repr__(self):
        return (f"<{self.name} q={self.q:.2f} N={self.N:.2f} "
                f"qeff={self.q_eff():.2f} {self.hits}/{self.uses}>")


def _clip(x, lo, hi):
    return lo if x < lo else (hi if x > hi else x)


# =====================================================================
# TEST 1 — "engel" kavraminin isim konmadan dogusu
# =====================================================================
def test_engel():
    print("=== TEST 1: engel kavrami ===")
    WALL = 7

    def world(x, a):
        nx = x + a
        return x if nx == WALL else nx      # duvara girilemez

    e = Edge(phi=lambda s, a: a == +1,
             psi=lambda s, a: s + 1,
             name="sag->+1")

    x = 2
    child = None
    for t in range(8):
        a = +1
        pred = e.predict(x, a)
        e.spend()
        nx = world(x, a)
        err = 0.0 if nx == pred else 1.0
        e.learn(err)
        e.tick()
        print(f"  t={t} x={x}->{nx} tahmin={pred} err={err:.0f}  {e}")

        if err > 0.5 and child is None:
            # phi'yi daralt: "hedef hucre bos olmali"
            child = e.specialize(lambda s, a: (s + a) != WALL,
                                 name="sag->+1 & hedef_bos")
            print(f"    >> YENI KENAR: {child.name}")
        x = nx

    print(f"  sonuc: ana kenar {e}")
    print(f"         cocuk     {child}\n")
    assert child is not None
    assert e.q < 0.5, "yanlis kenar zayiflamali"


# =====================================================================
# TEST 2 — N kesfi kendiliginden uretiyor mu
# =====================================================================
def test_kesif():
    print("=== TEST 2: N -> kesif ===")
    # Iki kenar ayni durumda aktif, ikisi de ayni q ile basliyor.
    # A yanlis, B dogru. Ayri bir kesif kodu YOK.
    A = Edge(lambda s, a: True, lambda s, a: "kapi_acilir", "A", q=0.60)
    B = Edge(lambda s, a: True, lambda s, a: "kutu_kayar",  "B", q=0.55)
    edges = [A, B]
    dogru = "kutu_kayar"

    secim = []
    for t in range(10):
        win = max(edges, key=lambda e: e.q_eff())
        secim.append(win.name)
        win.spend()
        err = 0.0 if win.predict(None, None) == dogru else 1.0
        win.learn(err)
        for e in edges:
            e.tick()
        print(f"  t={t} secilen={win.name} err={err:.0f}   "
              f"A(qeff={A.q_eff():.2f}) B(qeff={B.q_eff():.2f})")

    print(f"  secim dizisi: {' '.join(secim)}")
    print(f"  A={A}\n  B={B}\n")
    # Baslangicta A daha guclu olmasina ragmen B'ye gecilmeli
    assert secim[0] == "A", "basta yanlis kenar kazanmali"
    assert secim[-1] == "B", "sonda dogru kenara gecilmeli"
    assert B.q > A.q




# =====================================================================
# TEST 2b — N IZOLE EDILDI. DEVIR.md'nin "ASIL KANIT" dedigi test.
# Markdown'da anlatiliyordu ama KODDA YOKTU -> tek regresyonda sessizce
# kaybolurdu. Buraya alindi.
#
# Kurulum: iki kenar da HEP DOGRU (err=0 her zaman). Yani q hic dusmuyor.
# Tek fark yaratabilecek sey N. Klasik bir guncelleme A'da takilir kalir.
# =====================================================================
def test_kesif_izole():
    print("=== TEST 2b: N IZOLE (asil kanit) ===")

    def kosu(N_acik):
        A = Edge(lambda s, a: True, lambda s, a: "X", "A", q=0.60)
        B = Edge(lambda s, a: True, lambda s, a: "X", "B", q=0.55)
        edges = [A, B]
        dizi = []
        for t in range(12):
            w = max(edges, key=lambda e: e.q_eff())
            dizi.append(w.name)
            if N_acik:
                w.spend()
            w.learn(0.0)                 # HER IKISI DE DOGRU
            if N_acik:
                for e in edges:
                    e.tick()
        return dizi

    acik = kosu(True)
    kapali = kosu(False)
    print("  N ACIK  :", " ".join(acik))
    print("  N KAPALI:", " ".join(kapali))

    assert set(kapali) == {"A"}, "N kapaliyken sistem B'yi hic denememeli"
    assert "B" in acik, "N acikken sistem B'yi denemeli"
    print("  -> ayri kesif algoritmasi YOK; kesif kuralin kendi fiziginden.\n")



if __name__ == "__main__":
    test_engel()
    test_kesif()
    test_kesif_izole()
    print("uc test de gecti.")
