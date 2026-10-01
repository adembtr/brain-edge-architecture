"""
deney2.py — N'in GERCEKTEN fark yarattigi rejim.

DENEY 1-3'un dürüst sonucu: hata sinyali yanlis kurali hemen elerse
N hicbir sey katmiyor (greedy ile BIREBIR ayni sayilar). Yani onceki
deney N'i izole etmiyordu.

N'in tanimi geregi fark yaratmasi gereken rejim su:
    TAHMIN HATASI SECENEKLERI AYIRT EDEMIYOR.
Yani butun kurallar YEREL OLARAK DOGRU; hangisinin ilerleme sagladigi
yerel hatadan anlasilamiyor. ARC-AGI-3'teki durum tam olarak budur:
bircok tiklama gecerli bir kare degisimi uretir, ama sadece biri ilerletir.

Kurulum: K kural. HEPSI hep dogru tahmin ediyor (err=0 her zaman).
Gizli olarak sadece bir tanesi (g) ilerleme sagliyor. g periyodik degisiyor.
Olcut: kac adimda g bulunuyor; uzun kosuda toplam ilerleme.
"""
import math, random, json

def kosu(yontem, K=10, T=6000, periyot=600, tohum=0,
         alpha=0.30, Nmax=4.0, tau=3.0, eps=0.10, c=0.5):
    rnd = random.Random(tohum)
    q=[0.5]*K; N=[Nmax]*K; n_i=[0]*K; odul=[0.0]*K
    g = rnd.randrange(K)
    ilerleme=0; bulma_sureleri=[]; son_degisim=0; bulundu=False

    for t in range(T):
        if t % periyot == 0 and t > 0:
            yg = g
            while yg == g: yg = rnd.randrange(K)
            g = yg; son_degisim = t; bulundu = False

        if yontem=="greedy":       i = max(range(K), key=lambda j: q[j])
        elif yontem=="eps-greedy": i = rnd.randrange(K) if rnd.random()<eps else max(range(K), key=lambda j:q[j])
        elif yontem=="UCB1":
            i = max(range(K), key=lambda j: (odul[j]/n_i[j] + c*math.sqrt(2*math.log(t+1)/n_i[j])) if n_i[j]>0 else 1e9)
        elif yontem=="N-butce":    i = max(range(K), key=lambda j: q[j]*(N[j]/Nmax))

        # HEPSI DOGRU TAHMIN EDIYOR -> err=0 her zaman. q ayirt EDEMEZ.
        err = 0.0
        n_i[i]+=1
        q[i] = min(1.0, q[i] + alpha*(1-2*err))
        if i==g:
            ilerleme+=1; odul[i]+=1.0
            if not bulundu:
                bulma_sureleri.append(t-son_degisim); bulundu=True
        if yontem=="N-butce":
            N[i]=max(0.0,N[i]-1.0)
            for j in range(K): N[j]+= (Nmax-N[j])/tau
    ort_bulma = sum(bulma_sureleri)/len(bulma_sureleri) if bulma_sureleri else periyot
    return ilerleme, ort_bulma, len(bulma_sureleri)

YONTEMLER=["greedy","eps-greedy","UCB1","N-butce"]
TOHUMLAR=list(range(20))
DONEM = 6000//600

print("="*80)
print("DENEY 4 — HATA SINYALI AYIRT EDEMIYOR  (butun kurallar yerel olarak dogru)")
print("K=10 kural, gizli hedef her 600 adimda degisiyor, T=6000 (10 donem)")
print("="*80)
print(f"  {'yontem':<12}{'ilerleme':>11}{'std':>8}{'bulma suresi':>15}{'bulunan donem':>15}")
son={}
for y in YONTEMLER:
    r=[kosu(y,tohum=s) for s in TOHUMLAR]
    il=[x[0] for x in r]; bs=[x[1] for x in r]; bd=[x[2] for x in r]
    m=sum(il)/len(il); sd=(sum((v-m)**2 for v in il)/len(il))**0.5
    son[y]=(m,sd,sum(bs)/len(bs),sum(bd)/len(bd))
    print(f"  {y:<12}{m:>11.1f}{sd:>8.1f}{sum(bs)/len(bs):>15.1f}{sum(bd)/len(bd):>10.1f}/{DONEM}")

print()
print("="*80)
print("DENEY 5 — UZUN KOSU: UCB1'in kesif bonusu SONMEKTE mi? (T buyuyor)")
print("UCB bonusu ~ sqrt(ln t / n_i) -> n_i buyudukce SIFIRA gider (kalici).")
print("N ise DOLUYOR -> kesif hic bitmez. Fark uzun kosuda gorunmeli.")
print("="*80)
print(f"  {'T':>7}" + "".join(f"{y:>13}" for y in YONTEMLER) + "   (donem basina ilerleme)")
d5={}
for T in (2000, 6000, 20000, 60000):
    satir=[]
    for y in YONTEMLER:
        r=[kosu(y,T=T,tohum=s)[0] for s in TOHUMLAR]
        satir.append(sum(r)/len(r)/(T/600))
    d5[T]=dict(zip(YONTEMLER,satir))
    print(f"  {T:>7}" + "".join(f"{v:>13.1f}" for v in satir))

print()
print("="*80)
print("DENEY 6 — K'ye gore (degisen gizli hedef, hata sinyali yok)")
print("="*80)
print(f"  {'K':>4}" + "".join(f"{y:>13}" for y in YONTEMLER) + "   (ort bulma suresi, dusuk=iyi)")
d6={}
for K in (2,5,10,20,50):
    satir=[]
    for y in YONTEMLER:
        r=[kosu(y,K=K,tohum=s)[1] for s in TOHUMLAR]
        satir.append(sum(r)/len(r))
    d6[K]=dict(zip(YONTEMLER,satir))
    print(f"  {K:>4}" + "".join(f"{v:>13.1f}" for v in satir))

json.dump({"deney4":son,"deney5":d5,"deney6":d6},
          open("sonuclar2.json","w"), indent=1)
print("\nsonuclar2.json yazildi")
