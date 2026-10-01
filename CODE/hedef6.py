"""
hedef6.py — BAGLAM + HAFIZA + DUNYA MODELI.  (israr YOK -- olculdu, zarar veriyordu)

Degisiklikler (hedef4'e gore):
 1. ANAHTAR artik (token, BAGLAM_KODU, eylem).
    Ayni sekil + farkli cevre = FARKLI aday. Benzer cevre = kredi TRANSFER.
 2. Kredi ve dunya modeli BAGLAMLI KIMLIK vektoru uzerinden calisiyor.
 3. HAFIZA acik: her eylem + ise yarayanlar + seviye receteleri, oyuna ozel, diskte.
 4. NEDENSEL BAGLAM kaydediliyor: neye dokununca ne degisiyor.
 5. ISRAR YOK -- hedef5'te olculdu, 7 -> 4 seviye dusurmustu.
"""
import os, sys, random, json
from collections import defaultdict, Counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from nesne import nesneler, token, iliskiler, AGI, _kova
from uzaysal import UzaysalKredi
from model import UzaysalModel
from hafiza import Hafiza
from baglam import NedenselBaglam, sahne_nesneleri
from kimlik import baglam_kodu, kimlik_vek
import hedef as H0, hedef2 as H2, hedef3 as H3
from hedef4 import etki_im, YOK


def sahne_adaylari(o, K_komsu=3):
    """Aday anahtari: ((token, baglam_kodu), eylem)."""
    grid = o["grid"]; obs = nesneler(grid)
    eylemler = o["avail"] or [6]
    if obs:
        ic, dg, es = iliskiler(obs); kaba = Counter(token(x, 0, 0) for x in obs)
    else:
        ic = dg = es = []; kaba = None
    tokenlar = []
    for i, ob in enumerate(obs):
        yal = 1 if (kaba is not None and kaba[token(ob, 0, 0)] == 1) else 0
        tokenlar.append(token(ob, 0, 0, (ic[i], dg[i], es[i]), yal))
    nes = [(tokenlar[i], (float(ob.centroid[1]), float(ob.centroid[0])))
           for i, ob in enumerate(obs)]
    adaylar = defaultdict(list)
    kimlikler = []
    for i, ob in enumerate(obs):
        tk = tokenlar[i]
        bk = baglam_kodu(tk, nes[i][1], nes, K_komsu)      # <-- BAGLAM
        kim = (tk, bk)
        kimlikler.append(kim)
        hc = random.choice(sorted(ob.cells))
        for a2 in eylemler:
            adaylar[(kim, a2)].append((int(hc[1]), int(hc[0]), a2))
    return adaylar, obs, tokenlar, kimlikler


def kosu(oyun, butce=800, tohum=0, merak=0.35, olu_ceza=0.15,
         kapsama_esigi=40, hafiza=True, kayit_al=False):
    from env import Env
    random.seed(tohum)
    e = Env(oyun); o = e.reset()
    Hs = H0.hipotez_uret(o["grid"])
    tur_q = defaultdict(lambda: 0.6)
    kd  = UzaysalKredi(vek_fn=kimlik_vek)          # <-- BAGLAMLI KIMLIK
    mdl = UzaysalModel(vek_fn=kimlik_vek)          # <-- BAGLAMLI KIMLIK
    nb  = NedenselBaglam()
    aj = H3.UzaysalAjan(Hs, tur_q, kd)
    hf = Hafiza(oyun)
    if hafiza:
        hf.yukle()
    en_sv, ilk, t, sv_say = 0, None, 0, 0
    recete_kuyruk = list(hf.recete_adimlari()) if hafiza else []
    izler = []

    while t < butce:
        h = aj.sec_hipotez()
        obs0 = nesneler(o["grid"])
        m0 = h[1](obs0) if h else None
        if m0 is None:
            if h: aj.q[h[0]] = 0.0
            if all(aj.q[x[0]] <= 0.01 for x in Hs):
                Hs = H0.hipotez_uret(o["grid"])
                aj = H3.UzaysalAjan(Hs, tur_q, kd); h = None
        adaylar, obs, tokenlar, kimlikler = sahne_adaylari(o)
        if not adaylar:
            o = e.reset(); continue
        ad = h[0] if h else "-"
        kapi = len(mdl.kayit) >= kapsama_esigi

        def skor(kk):
            kim, a2 = kk
            temel = aj.kredi(ad, kk) + 0.3 * min(1.0, hf.ise_yarar_mi(kim, a2) / 20.0)
            tah, guv, kay = mdl.tahmin(kim, a2)
            if tah is None: return temel + merak
            if tah == YOK:  return temel * (olu_ceza if kapi else 0.8)
            return temel * (1.0 + 0.3 * guv)

        k = None
        while recete_kuyruk and k is None:
            aday = recete_kuyruk.pop(0)
            if aday in adaylar:
                k = aday
        if k is None:
            k = max(adaylar, key=lambda kk: skor(kk) * random.uniform(.95, 1.05))
        tah, guv, kayn = mdl.tahmin(k[0], k[1])

        cx, cy, a = random.choice(adaylar[k])
        onceki = o["grid"]
        o2 = e.step("click", a, cx, cy) if a == 6 else e.step("act", a)
        t += 1
        deg = sum(1 for y in range(len(onceki)) for x in range(len(onceki[0]))
                  if onceki[y][x] != o2["grid"][y][x])
        mdl.gozle(k[0], k[1], etki_im(onceki, o2["grid"]))
        hf.yaz(t, k[0], k[1], float(deg), o2["level"])

        # NEDENSEL BAGLAM: neye dokununca hangi tokenlar degisti
        if deg > 0:
            yeni_tok = set()
            for ob in nesneler(o2["grid"]):
                yeni_tok.add(token(ob, 0, 0))
            eski_tok = {tk[:7] if False else token(ob, 0, 0) for ob in obs}
            nb.gozle(k[0][0], list(yeni_tok ^ eski_tok)[:5])

        if kayit_al:
            izler.append(dict(t=t, kim=k[0], eylem=k[1], xy=(cx, cy),
                              hip=ad, mesafe=m0, tahmin=str(tah),
                              kaynak=kayn, deg=deg, sv=o2["level"],
                              grid=onceki))

        if o2["level"] > en_sv:
            en_sv = o2["level"]; ilk = ilk or t; sv_say += 1
            recete_kuyruk = list(hf.seviye_atladi())
            Hs = H0.hipotez_uret(o2["grid"])
            aj = H3.UzaysalAjan(Hs, tur_q, kd)
            o = o2
            continue

        m1 = h[1](nesneler(o2["grid"])) if h else None
        if h and m0 is not None and m1 is not None:
            dd = m1 - m0
            aj.ogren(ad, dd); aj.kredi_guncelle(ad, k, dd < 0)
        o = o2
        if o["state"] not in ("NOT_FINISHED", "NOT_STARTED"):
            o = e.reset()

    if hafiza:
        hf.kaydet()
    return dict(sv=en_sv, ilk=ilk, sv_say=sv_say, kayit=len(mdl.kayit),
                kimlik=len({k[0] for k in mdl.kayit}),
                nedensel=len(nb.bag), izler=izler)


if __name__ == "__main__":
    import hedef4 as H4
    oyunlar = sys.argv[1:] or ["lp85"]
    print("=" * 82)
    print("HEDEF6 = BAGLAM + HAFIZA + DUNYA MODELI  (israr yok)")
    print("=" * 82)
    print(f"  {'oyun':<7}{'RND':>5}{'H4':>4}{'HEDEF6':>8}{'sv_say':>7}"
          f"{'kimlik':>8}{'kayit':>7}{'nedensel':>10}{'ilk sv@':>9}")
    for g in oyunlar:
        r  = max(H0.rastgele(g, tohum=s) for s in (0, 1))
        n4 = max((H4.kosu(g, tohum=s) for s in (0, 1)), key=lambda d: d["sv"])
        n6s = [kosu(g, tohum=s) for s in (0, 1)]
        n6 = max(n6s, key=lambda d: d["sv"])
        il = [d["ilk"] for d in n6s if d["ilk"]]
        im = "  <--" if n6["sv"] > n4["sv"] else ("  (dustu)" if n6["sv"] < n4["sv"] else "")
        print(f"  {g:<7}{r:>5}{n4['sv']:>4}{n6['sv']:>8}{n6['sv_say']:>7}"
              f"{n6['kimlik']:>8}{n6['kayit']:>7}{n6['nedensel']:>10}"
              f"{(str(min(il)) if il else '-'):>9}{im}", flush=True)
