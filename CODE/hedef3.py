"""
hedef3.py — hedef2 + UZAY. Tek degisiklik: kredi TAM ESITLIK yerine BENZERLIK.

hedef2'de kredi (tur, token, eylem) ile tam esitlikte tutuluyordu; bir
token'da ogrenilen sey tek alani farkli token'a HIC gecmiyordu.
Burada UzaysalKredi devrede: hic denenmemis benzer token, benzerlerinin
kredisini DEVRALIR (K9: 0.50 -> 0.86).

Baska hicbir sey degismedi -- hipotezler, q/N fizigi, tur transferi ayni.
Boylece olculen fark SADECE uzaydan gelir.
"""
import os, sys, random, json
from collections import defaultdict, Counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from nesne import nesneler, token, iliskiler, AGI
from uzaysal import UzaysalKredi
import hedef as H0
import hedef2 as H2


class UzaysalAjan(H2.KaliciAjan):
    """KaliciAjan + benzerlik tabanli kredi."""

    def __init__(self, Hs, tur_q=None, kredi_deposu=None, **kw):
        super().__init__(Hs, tur_q=tur_q, tur_kredi=None, **kw)
        self.kd = kredi_deposu if kredi_deposu is not None else UzaysalKredi()

    def kredi(self, ad, k):
        tk, eylem = k
        return self.kd.oku(H2.tur_of(ad), tk, eylem)

    def kredi_guncelle(self, ad, k, iyi):
        tk, eylem = k
        self.kd.yaz(H2.tur_of(ad), tk, eylem, iyi)


def kosu(oyun, butce=800, tohum=0):
    from env import Env
    random.seed(tohum)
    e = Env(oyun); o = e.reset()
    Hs = H0.hipotez_uret(o["grid"])
    tur_q = defaultdict(lambda: 0.6)
    kd = UzaysalKredi()                     # <-- SEVIYELER ARASI YASAR
    aj = UzaysalAjan(Hs, tur_q, kd)
    en_sv, ilk, t = 0, None, 0
    sv_say = 0; tutan = set()

    while t < butce:
        h = aj.sec_hipotez()
        obs = nesneler(o["grid"])
        m0 = h[1](obs) if h else None
        if m0 is None:
            if h:
                aj.q[h[0]] = 0.0
            if all(aj.q[x[0]] <= 0.01 for x in Hs):
                Hs = H0.hipotez_uret(o["grid"])
                aj = UzaysalAjan(Hs, tur_q, kd)
                h = None
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
        k = max(adaylar, key=lambda kk: aj.kredi(ad, kk) * random.uniform(.9, 1.1))
        cx, cy, a = random.choice(adaylar[k])
        o2 = e.step("click", a, cx, cy) if a == 6 else e.step("act", a)
        t += 1

        if o2["level"] > en_sv:
            en_sv = o2["level"]; ilk = ilk or t; sv_say += 1
            Hs = H0.hipotez_uret(o2["grid"])
            aj = UzaysalAjan(Hs, tur_q, kd)      # HAFIZA + UZAY KORUNUR
            o = o2
            continue

        m1 = h[1](nesneler(o2["grid"])) if h else None
        if h and m0 is not None and m1 is not None:
            d = m1 - m0
            aj.ogren(ad, d)
            aj.kredi_guncelle(ad, k, d < 0)
            if d < 0:
                tutan.add(H2.tur_of(ad))
        o = o2
        if o["state"] not in ("NOT_FINISHED", "NOT_STARTED"):
            o = e.reset()

    return dict(sv=en_sv, ilk=ilk, hip=len(Hs), tutan=len(tutan),
                sv_say=sv_say, kayit=len(kd))


if __name__ == "__main__":
    oyunlar = sys.argv[1:] or sorted(os.listdir(os.environ["ENVIRONMENTS_DIR"]))
    print("=" * 78)
    print("HEDEF3 = hedef2 + UZAY (kredi tam esitlik yerine BENZERLIK)")
    print("Tek degisiklik. Fark varsa uzaydan gelir.")
    print("=" * 78)
    print(f"  {'oyun':<7}{'RND':>5}{'HEDEF2':>8}{'HEDEF3':>8}{'sv_say':>8}"
          f"{'kredi_kayit':>13}{'ilk sv@':>9}")
    tr = t2 = t3 = ust = 0; ozet = {}
    for g in oyunlar:
        try:
            r  = max(H0.rastgele(g, tohum=s) for s in (0, 1))
            n2 = max((H2.kosu(g, tohum=s) for s in (0, 1)), key=lambda d: d["sv"])
            n3s = [kosu(g, tohum=s) for s in (0, 1)]
        except Exception as ex:
            print(f"  {g:<7}  HATA {type(ex).__name__}: {str(ex)[:30]}", flush=True)
            continue
        n3 = max(n3s, key=lambda d: d["sv"])
        il = [d["ilk"] for d in n3s if d["ilk"]]
        im = "  <--" if n3["sv"] > n2["sv"] else ("  (dustu)" if n3["sv"] < n2["sv"] else "")
        ust += 1 if n3["sv"] > r else 0
        tr += r; t2 += n2["sv"]; t3 += n3["sv"]
        ozet[g] = dict(rnd=r, h2=n2["sv"], h3=n3["sv"])
        print(f"  {g:<7}{r:>5}{n2['sv']:>8}{n3['sv']:>8}{n3['sv_say']:>8}"
              f"{n3['kayit']:>13}{(str(min(il)) if il else '-'):>9}{im}", flush=True)
        json.dump(ozet, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "hedef3_ozet.json"),"w"), indent=1)
    print(f"\n  TOPLAM: rastgele {tr}   hedef2 {t2}   HEDEF3 {t3}")
