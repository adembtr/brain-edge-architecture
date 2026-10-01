"""
hedef4.py — hedef3 + UZAYSAL DUNYA MODELI.

Adem: "bir eylem dahi yaparsa bunu SONUCUYLA ogrenmeli ve kaydetmeli, ve
bunlari kullanarak DIGER EYLEMLERI TAHMIN etmeli. Eger bu olursa diger
asamalari rahat gecer."

hedef3'te uzay sadece KREDI icindi. Burada TAHMIN icin:
    her eylem sonucuyla modele yazilir  (tek gozlem)
    denenmemis cift icin model TAHMIN uretir (nesne/eylem benzerliginden)

Uc somut kullanim:
  1. OLU HAMLE ATLAMA : tahmin "hicbir sey olmaz" ise DENEMEDEN atla
     (solver_gorev.md'nin istedigi sey; skor (insan/ajan)^2 -> her bos
      eylem karesel ceza)
  2. MERAK            : tahmin YOKSA o cift bilgi getirir -> denemeye deger
  3. KREDI            : hedef3'teki benzerlik kredisi aynen duruyor
"""
import os, sys, random, json
from collections import defaultdict, Counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from nesne import nesneler, token, iliskiler, AGI, _kova
from uzaysal import UzaysalKredi
from model import UzaysalModel
import hedef as H0
import hedef2 as H2
import hedef3 as H3

YOK = ("yok",)


def etki_im(onceki, sonraki):
    d = sum(1 for y in range(len(onceki)) for x in range(len(onceki[0]))
            if onceki[y][x] != sonraki[y][x])
    return YOK if d == 0 else ("deg", _kova(d))


def kosu(oyun, butce=800, tohum=0, merak=0.35, olu_ceza=0.15):
    from env import Env
    random.seed(tohum)
    e = Env(oyun); o = e.reset()
    Hs = H0.hipotez_uret(o["grid"])
    tur_q = defaultdict(lambda: 0.6)
    kd = UzaysalKredi()
    mdl = UzaysalModel()                      # <-- DUNYA MODELI
    aj = H3.UzaysalAjan(Hs, tur_q, kd)
    en_sv, ilk, t, sv_say = 0, None, 0, 0
    atlanan = denenen = tahminli = 0

    while t < butce:
        h = aj.sec_hipotez()
        obs = nesneler(o["grid"])
        m0 = h[1](obs) if h else None
        if m0 is None:
            if h:
                aj.q[h[0]] = 0.0
            if all(aj.q[x[0]] <= 0.01 for x in Hs):
                Hs = H0.hipotez_uret(o["grid"])
                aj = H3.UzaysalAjan(Hs, tur_q, kd); h = None
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

        def skor(kk):
            tk2, a2 = kk
            temel = aj.kredi(ad, kk)
            tah, guven, kaynak = mdl.tahmin(tk2, a2)
            if tah is None:
                return temel + merak            # 2. MERAK: bilinmeyen bilgi getirir
            if tah == YOK:
                return temel * olu_ceza         # 1. OLU HAMLE: denemeden ele
            return temel * (1.0 + 0.3 * guven)

        k = max(adaylar, key=lambda kk: skor(kk) * random.uniform(.95, 1.05))
        tah_once = mdl.tahmin(k[0], k[1])
        if tah_once[2] is not None:
            tahminli += 1
        if tah_once[0] == YOK:
            atlanan += 1
        denenen += 1

        cx, cy, a = random.choice(adaylar[k])
        onceki = o["grid"]
        o2 = e.step("click", a, cx, cy) if a == 6 else e.step("act", a)
        t += 1

        # ---- TEK GOZLEM, SONUCUYLA KAYDEDILIR ----
        mdl.gozle(k[0], k[1], etki_im(onceki, o2["grid"]))

        if o2["level"] > en_sv:
            en_sv = o2["level"]; ilk = ilk or t; sv_say += 1
            Hs = H0.hipotez_uret(o2["grid"])
            aj = H3.UzaysalAjan(Hs, tur_q, kd)   # model VE kredi KORUNUR
            o = o2
            continue

        m1 = h[1](nesneler(o2["grid"])) if h else None
        if h and m0 is not None and m1 is not None:
            d = m1 - m0
            aj.ogren(ad, d)
            aj.kredi_guncelle(ad, k, d < 0)
        o = o2
        if o["state"] not in ("NOT_FINISHED", "NOT_STARTED"):
            o = e.reset()

    tokenlar = list({k[0] for k in mdl.kayit})[:40]
    ey = list({k[1] for k in mdl.kayit})
    top, den, tah = mdl.kapsama(tokenlar, ey) if tokenlar else (0, 0, 0)
    return dict(sv=en_sv, ilk=ilk, sv_say=sv_say, kayit=len(mdl.kayit),
                kapsama=(den + tah), top=top, tahminli=tahminli,
                atlanan=atlanan)


if __name__ == "__main__":
    oyunlar = sys.argv[1:] or sorted(os.listdir(os.environ["ENVIRONMENTS_DIR"]))
    print("=" * 84)
    print("HEDEF4 = hedef3 + DUNYA MODELI (tek gozlem -> cok tahmin)")
    print("olu hamleyi DENEMEDEN eler, bilinmeyeni merakla dener")
    print("=" * 84)
    print(f"  {'oyun':<7}{'RND':>5}{'H3':>4}{'HEDEF4':>8}{'sv_say':>7}"
          f"{'kayit':>7}{'kapsama':>9}{'tahminli%':>11}{'ilk sv@':>9}")
    tr = t3 = t4 = 0; ozet = {}
    for g in oyunlar:
        try:
            r  = max(H0.rastgele(g, tohum=s) for s in (0, 1))
            n3 = max((H3.kosu(g, tohum=s) for s in (0, 1)), key=lambda d: d["sv"])
            n4s = [kosu(g, tohum=s) for s in (0, 1)]
        except Exception as ex:
            print(f"  {g:<7}  HATA {type(ex).__name__}: {str(ex)[:30]}", flush=True)
            continue
        n4 = max(n4s, key=lambda d: d["sv"])
        il = [d["ilk"] for d in n4s if d["ilk"]]
        im = "  <--" if n4["sv"] > n3["sv"] else ("  (dustu)" if n4["sv"] < n3["sv"] else "")
        tr += r; t3 += n3["sv"]; t4 += n4["sv"]
        ozet[g] = dict(rnd=r, h3=n3["sv"], h4=n4["sv"])
        oran = 100.0 * n4["tahminli"] / max(1, n4["kayit"] + n4["tahminli"])
        print(f"  {g:<7}{r:>5}{n3['sv']:>4}{n4['sv']:>8}{n4['sv_say']:>7}"
              f"{n4['kayit']:>7}{n4['kapsama']:>4}/{n4['top']:<4}{oran:>10.0f}%"
              f"{(str(min(il)) if il else '-'):>9}{im}", flush=True)
        json.dump(ozet, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "hedef4_ozet.json"),"w"), indent=1)
    print(f"\n  TOPLAM: rastgele {tr}   hedef3 {t3}   HEDEF4 {t4}")
