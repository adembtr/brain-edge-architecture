"""
deney3.py — N'in FAZ GECISI. Makalenin ana teorik+deneysel sonucu.

TUREV
-----
Bir kenar surekli secilirse N'i su ozyinelemeyi izler:
    N_{t+1} = (N_t - 1) + (Nmax - (N_t - 1)) / tau
Sabit nokta:
    N* = Nmax + 1 - tau
Dolayisiyla surekli kullanilan kenarin ETKIN AGIRLIK TABANI:
    q_eff_taban = q_kullanilan * (Nmax + 1 - tau) / Nmax

Sistem baska bir kenari ANCAK su kosulda dener:
    q_kullanilan * (Nmax + 1 - tau) / Nmax  <  q_rakip

r = q_rakip / q_kullanilan  yazarsak KRITIK ZAMAN SABITI:
    tau* = Nmax (1 - r) + 1

tau <= tau*  -> kenar hic susmaz. KESIF YOK. (greedy ile ayni)
tau >  tau*  -> kenar susar, sira rakibe gecer. KESIF VAR.

Bu, Adem'in DEVIR.md'deki sezgisinin ("tau en kritik olan bu; cok kucuk ->
takintili ajan, cok buyuk -> dagi-nik ajan") kapali formu.
"""
import random, json

def kosu(K=10, T=6000, periyot=600, tohum=0, Nmax=4.0, tau=3.0,
         alpha=0.30, N_acik=True, q0=0.5):
    rnd=random.Random(tohum)
    q=[q0]*K; N=[Nmax]*K
    g=rnd.randrange(K); ilerleme=0; denenen=set()
    for t in range(T):
        if t%periyot==0 and t>0:
            yg=g
            while yg==g: yg=rnd.randrange(K)
            g=yg
        if N_acik: i=max(range(K), key=lambda j: q[j]*(N[j]/Nmax))
        else:      i=max(range(K), key=lambda j: q[j])
        denenen.add(i)
        q[i]=min(1.0,q[i]+alpha)          # HEPSI DOGRU -> err=0
        if i==g: ilerleme+=1
        if N_acik:
            N[i]=max(0.0,N[i]-1.0)
            for j in range(K): N[j]+=(Nmax-N[j])/tau
    return ilerleme, len(denenen)

def tau_kritik(Nmax, r): return Nmax*(1.0-r)+1.0

print("="*82)
print("DENEY 7 — FAZ GECISI. Nmax=4, rakip q=0.5, kullanilan q->1.0 => r=0.5")
print(f"          TEORI: tau* = Nmax(1-r)+1 = {tau_kritik(4,0.5):.2f}")
print("="*82)
print(f"  {'tau':>6}{'N*':>8}{'q_eff tabani':>15}{'ilerleme':>11}{'denenen kural':>16}")
sonuc={}
for tau in (1.5,2.0,2.5,3.0,3.25,3.5,4.0,5.0,6.0,8.0):
    Ns = 4.0+1.0-tau
    taban = 1.0*max(0.0,Ns)/4.0
    r=[kosu(tau=tau,tohum=s) for s in range(20)]
    il=sum(x[0] for x in r)/len(r); dn=sum(x[1] for x in r)/len(r)
    sonuc[tau]=(Ns,taban,il,dn)
    isaret = "  <-- KRITIK" if abs(tau-3.0)<1e-9 else ""
    print(f"  {tau:>6.2f}{Ns:>8.2f}{taban:>15.3f}{il:>11.1f}{dn:>12.1f}/10{isaret}")

r0=[kosu(N_acik=False,tohum=s) for s in range(20)]
print(f"\n  {'N YOK':>6}{'--':>8}{'--':>15}"
      f"{sum(x[0] for x in r0)/len(r0):>11.1f}{sum(x[1] for x in r0)/len(r0):>12.1f}/10")

print()
print("="*82)
print("DENEY 8 — TEORI DOGRULAMASI: farkli Nmax ve r icin tau* tahmini tutuyor mu?")
print("="*82)
print(f"  {'Nmax':>6}{'r':>6}{'teori tau*':>12}{'olculen esik':>15}{'uyum':>8}")
for Nmax in (3.0,4.0,6.0,10.0):
    for r in (0.3,0.5,0.7):
        teori = tau_kritik(Nmax,r)
        # olcum: tau'yu tarayip ilk kez >1 kural denenen yeri bul
        # r = q_rakip / q_kullanilan.  Kullanilan q -> 1.0 saturuyor,
        # rakipler baslangic q0'da kaliyor -> q0 = r.
        olculen=None
        t=1.0
        while t<=Nmax+2.0:
            rr=[kosu(tau=t,Nmax=Nmax,q0=r,tohum=s) for s in range(8)]
            if sum(x[1] for x in rr)/len(rr) > 1.05:
                olculen=t; break
            t+=0.125
        uyum = "OK" if olculen is not None and abs(olculen-teori)<=0.30 else "?"
        print(f"  {Nmax:>6.0f}{r:>6.1f}{teori:>12.2f}"
              f"{(f'{olculen:.2f}' if olculen else 'yok'):>15}{uyum:>8}")

json.dump({str(k):v for k,v in sonuc.items()}, open("faz.json","w"), indent=1)
print("\nfaz.json yazildi")
