"""
hedef2.py — SEVIYELER ARASI TRANSFER. Tek degisiklik, iki asamayi birden hedefler.

TESHIS: hedef.py'de seviye atlayinca `aj = HedefAjani(H)` yapiliyor ->
ogrenilmis butun eylem kredileri ve hipotez degerleri SILINIYOR.
Yani 2. asama (seviyeyi sonuna kadar goturme) yapisal olarak imkansiz.

AMA duz "hafizayi sakla" yetmez: seviye 2'de TOKENLER degisiyor, eski
hipotez ORNEGI gecersiz oluyor.

Adem'in m0r0 notu tam bunu soyluyor:
    sv1: "mavi onlari birbiriyle BIRLESTIRMEYE calisiyoruz"
    sv2: "siyah bes yollarin uzerinden tasiyip BIRBIRIYLE BIRLESTIRECEGIZ"
  Ayni TUR hedef, farkli nesneler.

=> Transfer edilecek sey hipotezin kendisi degil, TURU.
   ("birlestir" / "hizala" / "temizle" / "cogalt" / "esitle")

Ayni sey eylem kredisi icin de gecerli: kredi (hipotez_ornegi, token, eylem)
yerine (hipotez_TURU, token, eylem) ile tutulur. Token oyun-notr oldugu icin
seviyeler arasi anlamli kalir.
"""
import os, sys, random, json
from collections import defaultdict, Counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from nesne import nesneler, token, iliskiler, AGI
import hedef as H0


def tur_of(ad):
    """Hipotez adindan TURUNU cikar: 'birlestir_1234' -> 'birlestir'."""
    return ad.split("_")[0]


class KaliciAjan(H0.HedefAjani):
    """
    HedefAjani + SEVIYELER ARASI HAFIZA.

    tur_q     : hipotez TURUNUN degeri. Seviye/oyun degisse de yasar.
    tur_kredi : (tur, token, eylem) -> eylem kredisi. Token oyun-notr.

    Yeni seviyede hipotezler yeniden uretilir AMA q'lari sifirdan degil,
    TURLERININ gecmisinden tohumlanir. "Birlestirme ise yaramisti" bilgisi
    yeni seviyeye tasinir; hangi NESNELERI birlestirecegi yeniden ogrenilir.
    """

    def __init__(self, Hs, tur_q=None, tur_kredi=None, Nmax=6.0, tau=5.0,
                 alpha=0.30):
        super().__init__(Hs, Nmax=Nmax, tau=tau, alpha=alpha)
        self.tur_q = tur_q if tur_q is not None else defaultdict(lambda: 0.6)
        self.tur_kredi = (tur_kredi if tur_kredi is not None
                          else defaultdict(lambda: 0.5))
        # TOHUMLAMA: yeni hipotez, TURUNUN gecmisiyle baslar
        for h in Hs:
            self.q[h[0]] = self.tur_q[tur_of(h[0])]

    def ogren(self, ad, dmesafe):
        if ad not in self.q:
            return
        super().ogren(ad, dmesafe)
        # tur seviyesinde de ogren (daha yavas -> daha kalici)
        t = tur_of(ad)
        iyi = 1.0 if dmesafe < 0 else 0.0
        self.tur_q[t] = min(1.0, max(0.0,
                            self.tur_q[t] + 0.10 * (iyi - self.tur_q[t])))

    def kredi(self, ad, k):
        return self.tur_kredi[(tur_of(ad), k)]

    def kredi_guncelle(self, ad, k, iyi):
        anahtar = (tur_of(ad), k)
        self.tur_kredi[anahtar] = min(1.0, max(0.0, self.tur_kredi[anahtar]
                                      + 0.25 * (1.0 if iyi else -0.15)))


def kosu(oyun, butce=800, tohum=0):
    from env import Env
    random.seed(tohum)
    e = Env(oyun); o = e.reset()
    Hs = H0.hipotez_uret(o["grid"])
    tur_q = defaultdict(lambda: 0.6)          # <-- SEVIYELER ARASI YASAR
    tur_kredi = defaultdict(lambda: 0.5)      # <-- SEVIYELER ARASI YASAR
    aj = KaliciAjan(Hs, tur_q, tur_kredi)
    en_sv, ilk, t = 0, None, 0
    sv_anlari = []; tutan = set()

    while t < butce:
        h = aj.sec_hipotez()
        obs = nesneler(o["grid"])
        m0 = h[1](obs) if h else None
        if m0 is None:
            if h:
                aj.q[h[0]] = 0.0
            if all(aj.q[x[0]] <= 0.01 for x in Hs):
                Hs = H0.hipotez_uret(o["grid"])
                aj = KaliciAjan(Hs, tur_q, tur_kredi)   # HAFIZA KORUNUR
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
            en_sv = o2["level"]; ilk = ilk or t; sv_anlari.append(t)
            # ---- SEVIYE ATLADI: hipotezler yenilenir, HAFIZA KALIR ----
            Hs = H0.hipotez_uret(o2["grid"])
            aj = KaliciAjan(Hs, tur_q, tur_kredi)
            o = o2
            continue

        m1 = h[1](nesneler(o2["grid"])) if h else None
        if h and m0 is not None and m1 is not None:
            d = m1 - m0
            aj.ogren(ad, d)
            aj.kredi_guncelle(ad, k, d < 0)
            if d < 0:
                tutan.add(tur_of(ad))
        o = o2
        if o["state"] not in ("NOT_FINISHED", "NOT_STARTED"):
            o = e.reset()

    en_tur = max(tur_q.items(), key=lambda x: x[1]) if tur_q else ("-", 0)
    return dict(sv=en_sv, ilk=ilk, hip=len(Hs), tutan=len(tutan),
                sv_say=len(sv_anlari), en_tur=en_tur[0], en_tur_q=en_tur[1])


if __name__ == "__main__":
    oyunlar = sys.argv[1:] or sorted(os.listdir(os.environ["ENVIRONMENTS_DIR"]))
    print("=" * 80)
    print("HEDEF2 — SEVIYELER ARASI TRANSFER (hipotez TURU tasinir, ornegi degil)")
    print("Iki asama birden: (1) seviye gecmek  (2) gectikten sonra devam etmek")
    print("=" * 80)
    print(f"  {'oyun':<7}{'RND':>5}{'HEDEF2':>8}{'sv_say':>8}{'tutan_tur':>11}"
          f"{'en_iyi_tur':>13}{'q':>6}{'ilk sv@':>9}")
    tr = th = ust = 0; ozet = {}
    for g in oyunlar:
        try:
            r = max(H0.rastgele(g, tohum=s) for s in (0, 1))
            ns = [kosu(g, tohum=s) for s in (0, 1)]
        except Exception as ex:
            print(f"  {g:<7}  HATA {type(ex).__name__}: {str(ex)[:30]}", flush=True)
            continue
        n = max(ns, key=lambda d: d["sv"])
        il = [d["ilk"] for d in ns if d["ilk"]]
        im = "  <--" if n["sv"] > r else ""
        ust += 1 if n["sv"] > r else 0; tr += r; th += n["sv"]
        ozet[g] = dict(rnd=r, h2=n["sv"], tur=n["en_tur"])
        print(f"  {g:<7}{r:>5}{n['sv']:>8}{n['sv_say']:>8}{n['tutan']:>11}"
              f"{n['en_tur']:>13}{n['en_tur_q']:>6.2f}"
              f"{(str(min(il)) if il else '-'):>9}{im}", flush=True)
        json.dump(ozet, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "hedef2_ozet.json"),"w"), indent=1)
    print(f"\n  TOPLAM seviye: rastgele {tr}  ->  HEDEF2 {th}   ({ust}/{len(ozet)} ustun)")
