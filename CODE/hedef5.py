"""
hedef5.py — hedef4 + HAFIZA + ISRAR + SEVIYE RECETESI + olu-hamle KAPISI.

Adem'in dort talebi:
 1. ISRAR      "insan eylemi sona kadar goturur" -> degisim ureten eylem
               tukenene kadar tekrarlanir (salinim biter)
 2. HAFIZA     her eylem yazilir; ise yarayanlar AYRI dosyaya; HER OYUN AYRI
 3. RECETE     seviye gecince SON HALE bak -> o dizi recete; sonraki
               seviyede ONCE o denenir
 4. (benim ekim) OLU-HAMLE KAPISI: hedef4'te olu-hamle elemesi genisligi
    dusurmustu (bp35, cd82 kayboldu) cunku model zayif kanitla "burada bir
    sey olmaz" diyordu. Artik ceza SADECE model kapsamasi yeterliyse acilir.

Karar sirasi:
    1. RECETE adimi bekliyorsa    -> onu oyna
    2. ISRAR aktifse              -> ayni (token,eylem)i tekrarla
    3. yoksa                      -> skor (kredi + model + merak)
"""
import os, sys, random, json
from collections import defaultdict, Counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from nesne import nesneler, token, iliskiler, AGI, _kova
from uzaysal import UzaysalKredi
from model import UzaysalModel
from hafiza import Hafiza, Israrci
import hedef as H0, hedef2 as H2, hedef3 as H3
from hedef4 import etki_im, YOK


def kosu(oyun, butce=800, tohum=0, merak=0.35, olu_ceza=0.15,
         kapsama_esigi=40, hafiza_yaz=True, hafiza_yukle=True):
    from env import Env
    random.seed(tohum)
    e = Env(oyun); o = e.reset()
    Hs = H0.hipotez_uret(o["grid"])
    tur_q = defaultdict(lambda: 0.6); kd = UzaysalKredi(); mdl = UzaysalModel()
    aj = H3.UzaysalAjan(Hs, tur_q, kd)
    hf = Hafiza(oyun)
    if hafiza_yukle:
        hf.yukle()                       # ONCEKI KOSUNUN BILDIGIYLE BASLA
    iz = Israrci(sabir=2)
    recete_kuyruk = list(hf.recete_adimlari())    # onceki kosudan devralinan
    en_sv, ilk, t, sv_say = 0, None, 0, 0
    israr_adim = recete_adim = 0

    while t < butce:
        h = aj.sec_hipotez()
        obs = nesneler(o["grid"])
        m0 = h[1](obs) if h else None
        if m0 is None:
            if h: aj.q[h[0]] = 0.0
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
        # OLU-HAMLE KAPISI: model yeterince ogrenmeden ceza uygulanmaz
        kapi_acik = len(mdl.kayit) >= kapsama_esigi

        def skor(kk):
            tk2, a2 = kk
            temel = aj.kredi(ad, kk) + 0.4 * min(1.0, hf.ise_yarar_mi(tk2, a2) / 20.0)
            tah, guv, kay = mdl.tahmin(tk2, a2)
            if tah is None:  return temel + merak
            if tah == YOK:   return temel * (olu_ceza if kapi_acik else 0.8)
            return temel * (1.0 + 0.3 * guv)

        # ---- 1. RECETE  2. ISRAR  3. SKOR ----
        k = None; kaynak = "skor"
        while recete_kuyruk and k is None:
            aday = recete_kuyruk[0]
            if aday in adaylar:
                k = aday; kaynak = "recete"; recete_adim += 1
                recete_kuyruk.pop(0)
            else:
                recete_kuyruk.pop(0)
        if k is None:
            k = iz.onerir(adaylar)
            if k is not None:
                kaynak = "israr"; israr_adim += 1
        if k is None:
            k = max(adaylar, key=lambda kk: skor(kk) * random.uniform(.95, 1.05))

        cx, cy, a = random.choice(adaylar[k])
        onceki = o["grid"]
        o2 = e.step("click", a, cx, cy) if a == 6 else e.step("act", a)
        t += 1
        deg = sum(1 for y in range(len(onceki)) for x in range(len(onceki[0]))
                  if onceki[y][x] != o2["grid"][y][x])
        mdl.gozle(k[0], k[1], etki_im(onceki, o2["grid"]))
        hf.yaz(t, k[0], k[1], float(deg), o2["level"])

        if o2["level"] > en_sv:
            en_sv = o2["level"]; ilk = ilk or t; sv_say += 1
            iz.bildir(k, float(deg), True)          # seviye atlatan eylem YARARLI
            r = hf.seviye_atladi()                  # SON HALE BAK -> RECETE
            recete_kuyruk = list(r)                 # sonraki seviyede ONCE bunu dene
            iz.birak()
            Hs = H0.hipotez_uret(o2["grid"])
            aj = H3.UzaysalAjan(Hs, tur_q, kd)
            o = o2
            continue

        m1 = h[1](nesneler(o2["grid"])) if h else None
        yararli = None
        if h and m0 is not None and m1 is not None:
            dd = m1 - m0
            aj.ogren(ad, dd); aj.kredi_guncelle(ad, k, dd < 0)
            yararli = dd < 0                    # ISRAR: mesafeyi AZALTTI mi
        iz.bildir(k, float(deg), yararli)
        o = o2
        if o["state"] not in ("NOT_FINISHED", "NOT_STARTED"):
            o = e.reset()

    if hafiza_yaz:
        hf.kaydet()
    return dict(sv=en_sv, ilk=ilk, sv_say=sv_say, kayit=len(mdl.kayit),
                israr=israr_adim, recete=recete_adim,
                iy=len(hf._iy), rec_say=len(hf.receteler))


if __name__ == "__main__":
    import hedef4 as H4
    oyunlar = sys.argv[1:] or sorted(os.listdir(os.environ["ENVIRONMENTS_DIR"]))
    print("=" * 88)
    print("HEDEF5 = hedef4 + HAFIZA + ISRAR + RECETE + olu-hamle KAPISI")
    print("=" * 88)
    print(f"  {'oyun':<7}{'RND':>5}{'H4':>4}{'HEDEF5':>8}{'sv_say':>7}"
          f"{'israr':>7}{'recete':>7}{'ise_yarar':>10}{'ilk sv@':>9}")
    tr = t4 = t5 = 0; ozet = {}
    for g in oyunlar:
        try:
            r  = max(H0.rastgele(g, tohum=s) for s in (0, 1))
            n4 = max((H4.kosu(g, tohum=s) for s in (0, 1)), key=lambda d: d["sv"])
            n5s = [kosu(g, tohum=s) for s in (0, 1)]
        except Exception as ex:
            print(f"  {g:<7}  HATA {type(ex).__name__}: {str(ex)[:30]}", flush=True)
            continue
        n5 = max(n5s, key=lambda d: d["sv"])
        il = [d["ilk"] for d in n5s if d["ilk"]]
        im = "  <--" if n5["sv"] > n4["sv"] else ("  (dustu)" if n5["sv"] < n4["sv"] else "")
        tr += r; t4 += n4["sv"]; t5 += n5["sv"]
        ozet[g] = dict(rnd=r, h4=n4["sv"], h5=n5["sv"])
        print(f"  {g:<7}{r:>5}{n4['sv']:>4}{n5['sv']:>8}{n5['sv_say']:>7}"
              f"{n5['israr']:>7}{n5['recete']:>7}{n5['iy']:>10}"
              f"{(str(min(il)) if il else '-'):>9}{im}", flush=True)
        json.dump(ozet, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "hedef5_ozet.json"),"w"), indent=1)
    print(f"\n  TOPLAM: rastgele {tr}   hedef4 {t4}   HEDEF5 {t5}")
