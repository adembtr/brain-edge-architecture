"""
kayit.py — Ajanin her adimini kaydeder ve VIDEO uretir.

Her karede gorunen:
  sol  : oyunun karesi (ARC renkleri)
  sag  : ajanin O ANDA ne dusundugu
         - hangi hipotez aktif, mesafesi kac
         - hangi (token, eylem) secildi ve NEDEN (kredi / tahmin / merak)
         - model ne tahmin etmisti, GERCEK ne cikti
         - seviye, adim, kayit sayisi
Kirmizi "OLU TAHMIN" = model 'hicbir sey olmaz' dedi.
Yesil cerceve = seviye atlandi.
"""
import os, sys, random, subprocess
from collections import defaultdict, Counter
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from nesne import nesneler, token, iliskiler, AGI, _kova
from uzaysal import UzaysalKredi
from model import UzaysalModel
import hedef as H0, hedef2 as H2, hedef3 as H3
from hedef4 import etki_im, YOK

# ARC renk paleti (0-15)
PAL = [(0,0,0),(0,116,217),(255,65,54),(46,204,64),(255,220,0),
       (170,170,170),(240,18,190),(255,133,27),(127,219,255),(135,12,37),
       (85,85,85),(255,255,255),(160,80,240),(0,200,180),(200,120,60),(90,200,90)]
HUC = 8          # hucre boyutu piksel
PANEL = 420


def _font(b=13):
    for y in ("/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
              "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"):
        if os.path.exists(y):
            return ImageFont.truetype(y, b)
    return ImageFont.load_default()


F  = _font(13)
FB = _font(17)


def kare_ciz(grid, bilgi, seviye_atladi=False):
    H, W = len(grid), len(grid[0])
    im = Image.new("RGB", (W*HUC + PANEL, max(H*HUC, 560)), (18, 18, 22))
    d = ImageDraw.Draw(im)
    for y in range(H):
        for x in range(W):
            v = grid[y][x]
            d.rectangle([x*HUC, y*HUC, x*HUC+HUC-1, y*HUC+HUC-1],
                        fill=PAL[v % 16])
    if seviye_atladi:
        d.rectangle([0, 0, W*HUC-1, H*HUC-1], outline=(46, 204, 64), width=5)
    x0 = W*HUC + 14; y = 12
    for satir, renk, buyuk in bilgi:
        d.text((x0, y), satir, fill=renk, font=(FB if buyuk else F))
        y += 24 if buyuk else 18
    return im


def kosu_kaydet(oyun, butce=400, tohum=0, merak=0.35, olu_ceza=0.15,
                klasor=os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "VIDEO")):
    from env import Env
    random.seed(tohum)
    e = Env(oyun); o = e.reset()
    Hs = H0.hipotez_uret(o["grid"])
    tur_q = defaultdict(lambda: 0.6); kd = UzaysalKredi(); mdl = UzaysalModel()
    aj = H3.UzaysalAjan(Hs, tur_q, kd)
    en_sv, t = 0, 0
    kareler = []
    gecmis = []

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

        def skor(kk):
            tk2, a2 = kk
            temel = aj.kredi(ad, kk)
            tah, guv, kay = mdl.tahmin(tk2, a2)
            if tah is None:   return temel + merak
            if tah == YOK:    return temel * olu_ceza
            return temel * (1.0 + 0.3*guv)

        k = max(adaylar, key=lambda kk: skor(kk) * random.uniform(.95, 1.05))
        tah, guv, kayn = mdl.tahmin(k[0], k[1])
        cx, cy, a = random.choice(adaylar[k])
        onceki = o["grid"]
        o2 = e.step("click", a, cx, cy) if a == 6 else e.step("act", a)
        t += 1
        gercek = etki_im(onceki, o2["grid"])
        mdl.gozle(k[0], k[1], gercek)
        atladi = o2["level"] > en_sv

        # ---- kare ----
        neden = ("MERAK (bilinmiyor)" if tah is None else
                 ("OLU TAHMIN" if tah == YOK else f"tahmin {tah} g={guv:.2f}"))
        nrenk = ((255,220,0) if tah is None else
                 ((255,65,54) if tah == YOK else (46,204,64)))
        dogru = (tah == gercek)
        bilgi = [
            (f"{oyun}   adim {t}/{butce}", (255,255,255), True),
            (f"SEVIYE {o2['level']}" + ("   *** ATLADI ***" if atladi else ""),
             (46,204,64) if atladi else (200,200,200), True),
            ("", (0,0,0), False),
            ("HIPOTEZ (ilk kareden, geometri)", (140,190,255), False),
            (f"  {ad}", (255,255,255), False),
            (f"  mesafe: {m0 if m0 is not None else '-'}", (200,200,200), False),
            ("", (0,0,0), False),
            ("SECILEN", (140,190,255), False),
            (f"  eylem {k[1]}  @({cx},{cy})", (255,255,255), False),
            (f"  token renk={k[0][0]} gen={k[0][1]} uz={k[0][2]}", (180,180,180), False),
            (f"  kredi {aj.kredi(ad,k):.2f}", (180,180,180), False),
            ("", (0,0,0), False),
            ("NEDEN", (140,190,255), False),
            (f"  {neden}", nrenk, False),
            (f"  kaynak: {kayn or '-'}", (180,180,180), False),
            ("", (0,0,0), False),
            ("SONUC", (140,190,255), False),
            (f"  gercek: {gercek}", (255,255,255), False),
            (f"  {'TAHMIN TUTTU' if dogru and tah is not None else ('YENI BILGI' if tah is None else 'TAHMIN TUTMADI')}",
             (46,204,64) if (dogru and tah is not None) else (255,220,0), False),
            ("", (0,0,0), False),
            (f"model kaydi: {len(mdl.kayit)}", (150,150,150), False),
            (f"hipotez sayisi: {len(Hs)}", (150,150,150), False),
        ]
        kareler.append(kare_ciz(onceki, bilgi, atladi))
        gecmis.append((t, k[1], str(tah), str(gercek), o2["level"]))

        if atladi:
            en_sv = o2["level"]
            for _ in range(12):                    # seviye aninda duraklat
                kareler.append(kareler[-1])
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

    # ---- video ----
    os.makedirs(f"{klasor}/_kare", exist_ok=True)
    for i, im in enumerate(kareler):
        im.save(f"{klasor}/_kare/{i:05d}.png")
    cikti = f"{klasor}/{oyun}_sv{en_sv}.mp4"
    subprocess.run(["ffmpeg", "-y", "-framerate", "6", "-i",
                    f"{klasor}/_kare/%05d.png", "-c:v", "libx264",
                    "-pix_fmt", "yuv420p", "-vf", "scale=trunc(iw/2)*2:trunc(ih/2)*2",
                    cikti], capture_output=True)
    for f in os.listdir(f"{klasor}/_kare"):
        os.remove(f"{klasor}/_kare/{f}")
    with open(f"{klasor}/{oyun}_adimlar.txt", "w") as fh:
        fh.write("adim eylem tahmin gercek seviye\n")
        for r in gecmis:
            fh.write(" ".join(map(str, r)) + "\n")
    return cikti, en_sv, len(kareler)


if __name__ == "__main__":
    for oyun in (sys.argv[1:] or ["lp85"]):
        yol, sv, n = kosu_kaydet(oyun)
        print(f"{oyun}: seviye {sv}, {n} kare -> {yol}", flush=True)
