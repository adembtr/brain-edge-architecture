"""
asama2.py — 2. ASAMA TESTI: seviye gectikten sonra devam edebiliyor muyuz?

Bulgu: 800 eylem butcesiyle HICBIR oyunda 1'den fazla seviye gecilmedi
(hedef2 sv_say sutunu hep 1). Yani seviyeler-arasi transfer OLCULEMEDI --
transfer edilecek ikinci seviye hic gelmedi.

Bu test butceyi 800 -> 3000 cikarip soruyu ayirir:
    "2. asama neden olmuyor -- MEKANIZMA mi eksik, yoksa BUTCE mi?"

Sadece seviye 1'e ulasabilen oyunlarda kosulur (bosa CPU yok).
"""
import os, sys, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

OYUNLAR = ["vc33", "tn36", "r11l", "sp80", "lp85", "bp35", "cd82", "m0r0"]
BUTCE = int(os.environ.get("BUTCE", "3000"))

import cukur as C
import hedef2 as H2
import hedef as H0

print("=" * 78)
print(f"2. ASAMA — butce {BUTCE} (onceki testler 800'du)")
print("Soru: seviye 1'den sonra DEVAM edebiliyor muyuz?")
print("=" * 78)
print(f"  {'oyun':<7}{'RND':>5}{'CUKUR':>7}{'sv@':>7}{'HEDEF2':>8}{'sv_say':>8}{'sv@':>7}")
tr = tc = th = 0
ozet = {}
for g in OYUNLAR:
    try:
        r = max(H0.rastgele(g, butce=BUTCE, tohum=s) for s in (0,))
        c = C.kosu(g, butce=BUTCE, tohum=0)
        h = H2.kosu(g, butce=BUTCE, tohum=0)
    except Exception as ex:
        print(f"  {g:<7}  HATA {type(ex).__name__}: {str(ex)[:32]}", flush=True)
        continue
    tr += r; tc += c["sv"]; th += h["sv"]
    ozet[g] = dict(rnd=r, cukur=c["sv"], hedef2=h["sv"], sv_say=h["sv_say"])
    print(f"  {g:<7}{r:>5}{c['sv']:>7}{str(c['ilk'] or '-'):>7}"
          f"{h['sv']:>8}{h['sv_say']:>8}{str(h['ilk'] or '-'):>7}", flush=True)
    json.dump(ozet, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "asama2_ozet.json"),"w"), indent=1)
print(f"\n  TOPLAM: rastgele {tr}  cukur {tc}  hedef2 {th}   (butce {BUTCE})")
