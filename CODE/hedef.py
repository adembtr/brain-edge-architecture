"""
hedef.py — HEDEF HIPOTEZI. Ucuncu yontem (yenilik ve cukurdan farkli).

DEVIR.md §3 (Adem'in kendi gozlemi, "yer gercegi"):
    "Dogru hedef hipotezi ILK FRAME'DE, HIC EYLEM YAPMADAN, SAF GEOMETRIYLE
     olusuyor. Ajan bunu henuz taklit etmiyor."

Adem'in oyun notlari da bunu dogruluyor:
    m0r0: "bu mavi onlari siyah 5 yolunu kullanarak tasiyip BIRLESTIRECEK"
    ft09: "ortadaki kare etraftaki karelerin SABLONUNU temsil ediyor"
  Ikisi de ilk bakista, eylem yapmadan kurulmus hipotezler.

Yenilik (kesif.py) ve cukur (cukur.py) EYLEMDEN SONRA ogrenir.
Bu dosya EYLEMDEN ONCE hipotez kurar. Fark bu.

Hipotez = bir MESAFE fonksiyonu. 0 = saglandi. Ajan mesafeyi kucultmeye
calisir. Odul yok: mesafe dis dunyadan degil, SAHNENIN GEOMETRISINDEN
hesaplaniyor. Hipotez tutmuyorsa N tukenir, sira digerine gecer --
kenar fizigi hipotez seviyesinde.
"""
import os, sys, random, json
from collections import defaultdict, Counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from nesne import nesneler, token, iliskiler, degisim, etki, Ajan, AGI, P


def _kume(obs):
    """token -> o token'dan nesneler"""
    d = defaultdict(list)
    for ob in obs:
        d[token(ob, 0, 0)].append(ob)
    return d


def _merkez(ob):
    cy, cx = ob.centroid
    return (float(cx), float(cy))


def _uzaklik(a, b):
    ax, ay = _merkez(a); bx, by = _merkez(b)
    return abs(ax-bx) + abs(ay-by)


# =====================================================================
# HIPOTEZLER — hepsi SAF GEOMETRI, ilk kareden okunur
# =====================================================================
def h_birlestir(tk):
    """m0r0 tipi: ayni token'dan >=2 nesne -> onlari BIRLESTIR.
       mesafe = en yakin ikisinin uzakligi."""
    def f(obs):
        g = _kume(obs).get(tk, [])
        if len(g) < 2:
            return None
        return min(_uzaklik(a, b) for i, a in enumerate(g) for b in g[i+1:])
    return (f"birlestir_{abs(hash(tk))%99999}", f)


def h_temizle(tk):
    """Bu token'dan hic kalmasin. mesafe = adet."""
    def f(obs):
        n = len(_kume(obs).get(tk, []))
        return float(n) if n else None
    return (f"temizle_{abs(hash(tk))%99999}", f)


def h_esitle(t1, t2):
    """ft09 tipi: iki token'in adedi esitlensin. mesafe = |fark|."""
    def f(obs):
        k = _kume(obs)
        a, b = len(k.get(t1, [])), len(k.get(t2, []))
        if a == 0 and b == 0:
            return None
        return float(abs(a - b))
    return (f"esitle_{abs(hash((t1,t2)))%99999}", f)


def h_cogalt(tk):
    """Bu token'dan cok olsun. mesafe = -adet (kucultmek = cogaltmak)."""
    def f(obs):
        k = _kume(obs).get(tk, [])
        return -float(len(k)) if k else None
    return (f"cogalt_{abs(hash(tk))%99999}", f)


def h_hizala(tk):
    """Ayni token'dakiler ayni satir/sutuna gelsin."""
    def f(obs):
        g = _kume(obs).get(tk, [])
        if len(g) < 2:
            return None
        xs = [_merkez(o)[0] for o in g]; ys = [_merkez(o)[1] for o in g]
        return float(min(max(xs)-min(xs), max(ys)-min(ys)))
    return (f"hizala_{abs(hash(tk))%99999}", f)


def hipotez_uret(grid, ust=14):
    """
    ILK KAREDEN, HIC EYLEM YAPMADAN hipotezleri uret.
    Etiket yok, oyun bilgisi yok -- sadece token istatistigi ve geometri.
    """
    obs = nesneler(grid)
    k = _kume(obs)
    coklu = [t for t, g in k.items() if len(g) >= 2]
    tekil = [t for t, g in k.items() if len(g) == 1]
    H = []
    for t in coklu[:5]:
        H.append(h_birlestir(t)); H.append(h_hizala(t)); H.append(h_temizle(t))
    for t in tekil[:3]:
        H.append(h_cogalt(t))
    ts = sorted(k, key=lambda t: -len(k[t]))[:3]
    for i in range(len(ts)):
        for j in range(i+1, len(ts)):
            H.append(h_esitle(ts[i], ts[j]))
    return H[:ust]


# =====================================================================
class HedefAjani:
    """Hipotez seviyesinde kenar fizigi: q (tutuyor mu) + N (butce)."""

    def __init__(self, H, Nmax=6.0, tau=5.0, alpha=0.30):
        self.H = H
        self.q = {h[0]: 0.6 for h in H}
        self.N = {h[0]: Nmax for h in H}
        self.Nmax, self.tau, self.alpha = Nmax, tau, alpha
        self.aksiyon = defaultdict(lambda: 0.5)   # (hipotez, token, eylem)
        self.aktif = None

    def qe(self, ad):
        return self.q[ad] * (self.N[ad] / self.Nmax)

    def sec_hipotez(self):
        if not self.H:
            return None
        h = max(self.H, key=lambda x: self.qe(x[0]))
        self.aktif = h
        return h

    def ogren(self, ad, dmesafe):
        if ad not in self.q:          # hipotez kumesi yenilendi -> eski ad yok
            return
        """dmesafe < 0 = mesafe KUCULDU = hipotez ise yariyor."""
        iyi = 1.0 if dmesafe < 0 else 0.0
        self.q[ad] = min(1.0, max(0.0, self.q[ad] + self.alpha*(iyi - self.q[ad])))
        self.N[ad] = max(0.0, self.N[ad] - 1.0)
        for a in self.N:
            self.N[a] += (self.Nmax - self.N[a]) / self.tau


def kosu(oyun, butce=800, tohum=0):
    from env import Env
    random.seed(tohum)
    e = Env(oyun); o = e.reset()
    H = hipotez_uret(o["grid"])          # <-- ILK KARE, EYLEM YOK
    aj = HedefAjani(H)
    kenar = Ajan()
    en_sv, ilk, t = 0, None, 0
    tutan = set()

    while t < butce:
        h = aj.sec_hipotez()
        obs = nesneler(o["grid"])
        m0 = h[1](obs) if h else None
        if m0 is None:                    # hipotez artik gecersiz -> sustur
            if h:
                aj.q[h[0]] = 0.0
            if all(aj.q[x[0]] <= 0.01 for x in H):
                H = hipotez_uret(o["grid"])   # yeniden hipotez kur
                aj = HedefAjani(H); h = None
            # yine de bir adim at (bos gecme)
        eylemler = o["avail"] or [6]
        if obs:
            ic, dg, es = iliskiler(obs); kaba = Counter(token(x,0,0) for x in obs)
        else:
            ic = dg = es = []; kaba = None
        adaylar = defaultdict(list)
        for i, ob in enumerate(obs):
            yal = 1 if (kaba is not None and kaba[token(ob,0,0)] == 1) else 0
            tk = token(ob, 0, 0, (ic[i], dg[i], es[i]), yal)
            hc = random.choice(sorted(ob.cells))
            for a2 in eylemler:
                adaylar[(tk, a2)].append((int(hc[1]), int(hc[0]), a2))
        if not adaylar:
            o = e.reset(); continue

        ad = h[0] if h else "-"
        k = max(adaylar, key=lambda kk: aj.aksiyon[(ad, kk)] * random.uniform(0.9, 1.1))
        cx, cy, a = random.choice(adaylar[k])
        o2 = e.step("click", a, cx, cy) if a == 6 else e.step("act", a)
        t += 1
        if o2["level"] > en_sv:
            en_sv = o2["level"]; ilk = ilk or t
            H = hipotez_uret(o2["grid"]); aj = HedefAjani(H)   # yeni seviye, yeni hipotez
            h = None
        m1 = h[1](nesneler(o2["grid"])) if h else None
        if h and m0 is not None and m1 is not None:
            d = m1 - m0
            aj.ogren(ad, d)
            # eylem kredisi: mesafeyi kuculten (token,eylem) guclenir
            aj.aksiyon[(ad, k)] = min(1.0, max(0.0,
                aj.aksiyon[(ad, k)] + 0.25 * (1.0 if d < 0 else -0.15)))
            if d < 0:
                tutan.add(ad)
        o = o2
        if o["state"] not in ("NOT_FINISHED", "NOT_STARTED"):
            o = e.reset()
    return dict(sv=en_sv, ilk=ilk, hip=len(H), tutan=len(tutan),
                en_iyi=max([aj.q[x[0]] for x in H] or [0]))


def rastgele(oyun, butce=800, tohum=0):
    from env import Env
    rnd = random.Random(tohum); e = Env(oyun); o = e.reset(); sv = 0
    H_, W_ = len(o["grid"]), len(o["grid"][0])
    for _ in range(butce):
        a = rnd.choice(o["avail"] or [6])
        o = (e.step("click", a, rnd.randrange(W_), rnd.randrange(H_))
             if a == 6 else e.step("act", a))
        sv = max(sv, o["level"])
        if o["state"] not in ("NOT_FINISHED", "NOT_STARTED"):
            o = e.reset()
    return sv


if __name__ == "__main__":
    oyunlar = sys.argv[1:] or sorted(os.listdir(os.environ["ENVIRONMENTS_DIR"]))
    print("=" * 76)
    print("HEDEF HIPOTEZI — ilk kareden, EYLEM YAPMADAN, saf geometriyle")
    print("(DEVIR.md §3: 'ajan bunu henuz taklit etmiyor')")
    print("=" * 76)
    print(f"  {'oyun':<7}{'RND':>5}{'HEDEF':>7}{'hipotez':>9}{'tutan':>7}"
          f"{'en_iyi_q':>10}{'ilk sv@':>9}")
    tr = th = ust = 0; ozet = {}
    for g in oyunlar:
        try:
            r = max(rastgele(g, tohum=s) for s in (0, 1))
            ns = [kosu(g, tohum=s) for s in (0, 1)]
        except Exception as ex:
            print(f"  {g:<7}  HATA {type(ex).__name__}: {str(ex)[:32]}", flush=True)
            continue
        n = max(ns, key=lambda d: d["sv"])
        il = [d["ilk"] for d in ns if d["ilk"]]
        im = "  <--" if n["sv"] > r else ""
        ust += 1 if n["sv"] > r else 0; tr += r; th += n["sv"]
        ozet[g] = dict(rnd=r, hedef=n["sv"], tutan=n["tutan"])
        print(f"  {g:<7}{r:>5}{n['sv']:>7}{n['hip']:>9}{n['tutan']:>7}"
              f"{n['en_iyi']:>10.2f}{(str(min(il)) if il else '-'):>9}{im}", flush=True)
        json.dump(ozet, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "hedef_ozet.json"),"w"), indent=1)
    print(f"\n  TOPLAM seviye: rastgele {tr}  ->  HEDEF {th}   ({ust}/{len(ozet)} ustun)")
