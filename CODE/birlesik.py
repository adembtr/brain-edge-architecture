"""
birlesik.py — CUKUR + HEDEF. Dorduncu yontem.

Ikisi de bagimsiz olarak kazandirdi ama her biri otekinin eksigi:
    CUKUR : eylem dizisi biriktiriyor, ama NEYE DOGRU bilmiyor
            (korlemesine "degisim buyuk olsun" diyor)
    HEDEF : yon veriyor, ama tek eylemle calisiyor (dizi kuramiyor)

Birlesim:
    hipotez (ilk kareden, saf geometri)  ->  YON
    cukur   (eylem dizisi)               ->  ARAC
    cukurun degeri = ham degisim DEGIL, HIPOTEZIN MESAFESINI ne kadar
    azalttigi. Yani cukur artik bir HEDEFE hizmet ediyor.

Adem'in oyun notlarindaki insan davranisi da bu:
    m0r0: once hipotez ("mavi 10'lari birlestirecegiz"), sonra dizi
          ("sag-sag-asagi ile tasi, duvara dayat, otekini getir")
Hipotez olmadan dizi anlamsiz; dizi olmadan hipotez uygulanamaz.
"""
import os, sys, random, json
from collections import defaultdict, Counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from nesne import nesneler, token, iliskiler, Ajan, AGI
from hedef import hipotez_uret, HedefAjani
from cukur import Cukur, Kase


def _adaylar(o):
    grid = o["grid"]; obs = nesneler(grid)
    eylemler = o["avail"] or [6]
    if obs:
        ic, dg, es = iliskiler(obs); kaba = Counter(token(x, 0, 0) for x in obs)
    else:
        ic = dg = es = []; kaba = None
    ad = defaultdict(list)
    for i, ob in enumerate(obs):
        yal = 1 if (kaba is not None and kaba[token(ob, 0, 0)] == 1) else 0
        tk = token(ob, 0, 0, (ic[i], dg[i], es[i]), yal)
        h = random.choice(sorted(ob.cells))
        for a2 in eylemler:
            ad[(tk, a2)].append((int(h[1]), int(h[0]), a2))
    return ad, frozenset(k[0] for k in ad), obs


def kosu(oyun, butce=800, tohum=0, pencere=3):
    from env import Env
    random.seed(tohum)
    e = Env(oyun); o = e.reset()
    H = hipotez_uret(o["grid"])              # ILK KARE, eylem yok
    haj = HedefAjani(H)
    kaj = Ajan()
    kaseler = defaultdict(Kase)              # hipotez adi -> kendi cukurlari
    en_sv, ilk, t = 0, None, 0
    tampon = []; son_c = None; kuru = 0

    def olc(h, obs):
        try:
            return h[1](obs)
        except Exception:
            return None

    while t < butce:
        adaylar, sahne, obs = _adaylar(o)
        if not adaylar:
            o = e.reset(); continue
        h = haj.sec_hipotez()
        if h is None:
            H = hipotez_uret(o["grid"]); haj = HedefAjani(H); continue
        ad = h[0]; m0 = olc(h, obs)
        if m0 is None:                        # hipotez gecersizlesti
            haj.q[ad] = 0.0
            if all(haj.q[x[0]] <= 0.01 for x in H):
                H = hipotez_uret(o["grid"]); haj = HedefAjani(H)
            continue
        kase = kaseler[ad]

        # ---- 1. Bu hipoteze hizmet eden bir CUKUR var mi? ----
        uygun = [c for c in kase.uygun(sahne) if c.q_eff() > 0.30 and c.psi > 0]
        girildi = False
        if uygun:
            c = max(uygun, key=lambda c: c.deger())
            girildi = True; c.harca(); basla = m0
            for i_k, k in enumerate(c.govde):
                if t >= butce or k not in adaylar:
                    break
                cx, cy, a = random.choice(adaylar[k])
                o = e.step("click", a, cx, cy) if a == 6 else e.step("act", a)
                t += 1
                if o["level"] > en_sv:
                    en_sv = o["level"]; ilk = ilk or t
                    H = hipotez_uret(o["grid"]); haj = HedefAjani(H)
                    kaseler = defaultdict(Kase); break
                if o["state"] not in ("NOT_FINISHED", "NOT_STARTED"):
                    o = e.reset(); break
                adaylar, sahne, obs = _adaylar(o)
                m_ara = olc(h, obs)
                if i_k >= 1 and m_ara is not None and m_ara >= basla:
                    break                      # ise yaramiyor -> erken cikis
            son = olc(h, nesneler(o["grid"]))
            kazanc = (basla - son) if (son is not None) else 0.0
            c.ogren(max(0.0, kazanc))          # CUKUR MESAFEYE gore ogrenir
            haj.ogren(ad, -kazanc)
            tampon = []
            son_c = c if kazanc > 0 else None
            kuru = 0 if kazanc > 0 else kuru + 1

        # ---- 2. Cukur yoksa: tek adim kesif, mesafeye gore kredi ----
        if not girildi:
            k = max(adaylar, key=lambda kk:
                    haj.aksiyon[(ad, kk)] * kaj.q_eff(kk) * random.uniform(.9, 1.1)
                    if hasattr(kaj, "q_eff") else haj.aksiyon[(ad, kk)])
            cx, cy, a = random.choice(adaylar[k])
            kaj.harca(k); kaj.tik(list(adaylar.keys()))
            o = e.step("click", a, cx, cy) if a == 6 else e.step("act", a)
            t += 1
            if o["level"] > en_sv:
                en_sv = o["level"]; ilk = ilk or t
                H = hipotez_uret(o["grid"]); haj = HedefAjani(H)
                kaseler = defaultdict(Kase); tampon = []; continue
            if o["state"] not in ("NOT_FINISHED", "NOT_STARTED"):
                o = e.reset(); tampon = []; continue
            m1 = olc(h, nesneler(o["grid"]))
            d = (m0 - m1) if (m1 is not None) else 0.0     # d>0 = mesafe AZALDI
            haj.ogren(ad, -d)
            haj.aksiyon[(ad, k)] = min(1.0, max(0.0, haj.aksiyon[(ad, k)]
                                                + 0.25*(1.0 if d > 0 else -0.15)))
            tampon.append((sahne, k, d))
            if len(tampon) >= pencere:
                kaz = sum(x[2] for x in tampon)
                if kaz > 0:                     # ---- MESAFEYI AZALTAN DIZI = CUKUR
                    c = kase.dogur(tampon[0][0], [x[1] for x in tampon], kaz, t)
                    if c is not None and son_c is not None:
                        kase.birlestir(son_c, c, t)
                    son_c = c; kuru = 0
                else:
                    kuru += 1
                    for kk in [x[1] for x in tampon]:
                        kaj.N[kk] = max(0.0, kaj.N[kk] - 1.0)
                tampon = []
        for c in kase.cukurlar:
            c.tik()
        if t % 50 == 0:
            kase.buda()

    tc = sum(len(k.cukurlar) for k in kaseler.values())
    tb = sum(k.birlesme for k in kaseler.values())
    tutan = sum(1 for x in H if haj.q.get(x[0], 0) > 0.5)
    return dict(sv=en_sv, ilk=ilk, hip=len(H), cukur=tc, birles=tb, tutan=tutan)


def rastgele(oyun, butce=800, tohum=0):
    from env import Env
    rnd = random.Random(tohum); e = Env(oyun); o = e.reset(); sv = 0
    Hh, Ww = len(o["grid"]), len(o["grid"][0])
    for _ in range(butce):
        a = rnd.choice(o["avail"] or [6])
        o = (e.step("click", a, rnd.randrange(Ww), rnd.randrange(Hh))
             if a == 6 else e.step("act", a))
        sv = max(sv, o["level"])
        if o["state"] not in ("NOT_FINISHED", "NOT_STARTED"):
            o = e.reset()
    return sv


if __name__ == "__main__":
    oyunlar = sys.argv[1:] or sorted(os.listdir(os.environ["ENVIRONMENTS_DIR"]))
    print("=" * 74)
    print("BIRLESIK — hipotez YON verir, cukur ARAC olur.")
    print("Cukurun degeri: ham degisim degil, HIPOTEZIN MESAFESINI azaltmasi.")
    print("=" * 74)
    print(f"  {'oyun':<7}{'RND':>5}{'BIRL':>6}{'hip':>5}{'cukur':>7}"
          f"{'birles':>8}{'tutan':>7}{'ilk sv@':>9}")
    tr = tb = ust = 0; ozet = {}
    for g in oyunlar:
        try:
            r = max(rastgele(g, tohum=s) for s in (0, 1))
            ns = [kosu(g, tohum=s) for s in (0, 1)]
        except Exception as ex:
            print(f"  {g:<7}  HATA {type(ex).__name__}: {str(ex)[:30]}", flush=True)
            continue
        n = max(ns, key=lambda d: d["sv"])
        il = [d["ilk"] for d in ns if d["ilk"]]
        im = "  <--" if n["sv"] > r else ""
        ust += 1 if n["sv"] > r else 0; tr += r; tb += n["sv"]
        ozet[g] = dict(rnd=r, birl=n["sv"])
        print(f"  {g:<7}{r:>5}{n['sv']:>6}{n['hip']:>5}{n['cukur']:>7}"
              f"{n['birles']:>8}{n['tutan']:>7}"
              f"{(str(min(il)) if il else '-'):>9}{im}", flush=True)
        json.dump(ozet, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "birlesik_ozet.json"),"w"), indent=1)
    print(f"\n  TOPLAM seviye: rastgele {tr}  ->  BIRLESIK {tb}   ({ust}/{len(ozet)} ustun)")
