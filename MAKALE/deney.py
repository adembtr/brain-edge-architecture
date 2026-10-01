"""
deney.py — Makale icin ana deney.

Soru: sinaps-yerel bir KULLANIM BUTCESI (N), ayri bir kesif algoritmasi
olmadan kesif uretebilir mi? Ve klasik kesif yontemlerine kiyasla nerede
durur -- ozellikle DEGISEN dunyada?

Kiyaslananlar (hepsi ayni gorevde, ayni tohumlarda):
  greedy    : argmax q                        (kesif yok)
  eps-greedy: e olasilikla rastgele            (kesif = dis gurultu)
  UCB1      : argmax q + c*sqrt(2 ln t / n_i)  (kesif = GLOBAL sayac bonusu)
  N-butce   : argmax q * (N_i / Nmax)          (kesif = KURALIN IC DURUMU)

Gorev: K kural, biri dogru. T/2 aninda DOGRU KURAL DEGISIR (durağan degil).
Olcut: toplam hata, ve degisimden sonra toparlanma suresi.
"""
import math, os, random, json


def kosu(yontem, K=10, T=4000, degisim=True, tohum=0,
         alpha=0.30, Nmax=4.0, tau=3.0, eps=0.10, c=0.5):
    rnd = random.Random(tohum)
    q = [0.5] * K
    N = [Nmax] * K
    n_i = [0] * K
    dogru = rnd.randrange(K)
    yeni_dogru = dogru
    while yeni_dogru == dogru:
        yeni_dogru = rnd.randrange(K)

    hatalar = 0
    toparlanma = None
    dogru_seri = 0
    for t in range(T):
        if degisim and t == T // 2:
            dogru = yeni_dogru
            dogru_seri = 0

        if yontem == "greedy":
            i = max(range(K), key=lambda j: q[j])
        elif yontem == "eps-greedy":
            i = rnd.randrange(K) if rnd.random() < eps else max(range(K), key=lambda j: q[j])
        elif yontem == "UCB1":
            i = max(range(K), key=lambda j: q[j] + c * math.sqrt(
                2 * math.log(t + 1) / n_i[j]) if n_i[j] > 0 else 1e9)
        elif yontem == "N-butce":
            i = max(range(K), key=lambda j: q[j] * (N[j] / Nmax))
        else:
            raise ValueError(yontem)

        err = 0.0 if i == dogru else 1.0
        hatalar += err
        n_i[i] += 1
        q[i] = min(1.0, max(0.0, q[i] + alpha * (1 - 2 * err)))
        if yontem == "N-butce":
            N[i] = max(0.0, N[i] - 1.0)
            N[i] = min(Nmax, N[i] + 1.0 * err)
            for j in range(K):
                N[j] += (Nmax - N[j]) / tau

        if degisim and t >= T // 2:
            dogru_seri = dogru_seri + 1 if err == 0 else 0
            if toparlanma is None and dogru_seri >= 20:
                toparlanma = t - T // 2 - 19
    return hatalar, (toparlanma if toparlanma is not None else T // 2)


YONTEMLER = ["greedy", "eps-greedy", "UCB1", "N-butce"]
TOHUMLAR = list(range(20))

print("=" * 78)
print("DENEY 1 — DURAGAN dunya (dogru kural degismiyor), K=10, T=4000")
print("=" * 78)
print(f"  {'yontem':<12}{'ort hata':>11}{'std':>9}")
d1 = {}
for y in YONTEMLER:
    hs = [kosu(y, degisim=False, tohum=s)[0] for s in TOHUMLAR]
    m = sum(hs) / len(hs)
    sd = (sum((h - m) ** 2 for h in hs) / len(hs)) ** 0.5
    d1[y] = (m, sd)
    print(f"  {y:<12}{m:>11.1f}{sd:>9.1f}")

print()
print("=" * 78)
print("DENEY 2 — DEGISEN dunya (T/2'de dogru kural degisir)  <-- ASIL SORU")
print("=" * 78)
print(f"  {'yontem':<12}{'ort hata':>11}{'std':>9}{'toparlanma':>13}{'std':>9}")
d2 = {}
for y in YONTEMLER:
    r = [kosu(y, degisim=True, tohum=s) for s in TOHUMLAR]
    hs = [x[0] for x in r]; ts = [x[1] for x in r]
    m = sum(hs) / len(hs); sd = (sum((h - m) ** 2 for h in hs) / len(hs)) ** 0.5
    mt = sum(ts) / len(ts); sdt = (sum((x - mt) ** 2 for x in ts) / len(ts)) ** 0.5
    d2[y] = (m, sd, mt, sdt)
    print(f"  {y:<12}{m:>11.1f}{sd:>9.1f}{mt:>13.1f}{sdt:>9.1f}")

print()
print("=" * 78)
print("DENEY 3 — K'ye gore olcekleme (degisen dunya)")
print("=" * 78)
print(f"  {'K':>4}" + "".join(f"{y:>13}" for y in YONTEMLER))
d3 = {}
for K in (2, 5, 10, 20, 50):
    satir = []
    for y in YONTEMLER:
        hs = [kosu(y, K=K, degisim=True, tohum=s)[0] for s in TOHUMLAR]
        satir.append(sum(hs) / len(hs))
    d3[K] = dict(zip(YONTEMLER, satir))
    print(f"  {K:>4}" + "".join(f"{v:>13.1f}" for v in satir))

json.dump({"duragan": d1, "degisen": d2, "olcekleme": d3},
          open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "sonuclar.json"), "w"), indent=1)
print("\nsonuclar.json yazildi")
