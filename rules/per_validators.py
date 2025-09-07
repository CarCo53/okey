# rules/per_validators.py
from itertools import combinations
from log import logger

@logger.log_function
def kut_mu(taslar, min_sayi=3):
    if len(taslar) < min_sayi: return False
    degerler = set()
    renkler = set()
    for t in taslar:
        gercek_tas = t.joker_yerine_gecen or t
        if gercek_tas.renk == "joker": continue
        degerler.add(gercek_tas.deger)
        renkler.add(gercek_tas.renk)
    if len(renkler) != len([t for t in taslar if (t.joker_yerine_gecen or t.renk != "joker")]):
        return False
    return len(degerler) <= 1 and min_sayi <= len(taslar) <= 4

@logger.log_function
def seri_mu(taslar, min_sayi=3):
    if len(taslar) < min_sayi: return False
    renk, sayilar, joker_sayisi = None, [], 0
    for t in taslar:
        gercek_tas = t.joker_yerine_gecen or t
        if t.renk == "joker" and not t.joker_yerine_gecen:
            joker_sayisi += 1
            continue
        if renk is None: renk = gercek_tas.renk
        elif gercek_tas.renk != renk: return False
        sayilar.append(gercek_tas.deger)
    if not sayilar: return joker_sayisi >= min_sayi
    if len(set(sayilar)) != len(sayilar): return False
    sayilar.sort()

    # Serideki boşlukları hesaplama (1-13 döngüsü hariç)
    gaps_linear = 0
    for i in range(len(sayilar) - 1):
        gap = sayilar[i+1] - sayilar[i] - 1
        if gap < 0: # Duplicates found
            return False
        gaps_linear += gap
    
    # Normal seri kontrolü
    if joker_sayisi >= gaps_linear:
        return True

    # Döngüsel seri (12-13-1 gibi) kontrolü
    if 1 in sayilar and 13 in sayilar:
        dongusel_sayilar = sorted([14 if s == 1 else s for s in sayilar])
        gaps_dongusel = 0
        for i in range(len(dongusel_sayilar) - 1):
            gap = dongusel_sayilar[i+1] - dongusel_sayilar[i] - 1
            if gap < 0: # Duplicates found in dongusel
                 return False
            gaps_dongusel += gap
        return joker_sayisi >= gaps_dongusel

    return False
@logger.log_function
def coklu_per_dogrula(taslar, tip, min_sayi, adet):
    if len(taslar) != min_sayi * adet: return False
    kontrol_fonksiyonu = kut_mu if tip == "küt" else seri_mu
    for grup1_kombinasyonu in combinations(taslar, min_sayi):
        kalan_taslar = [t for t in taslar if t not in grup1_kombinasyonu]
        if kontrol_fonksiyonu(list(grup1_kombinasyonu), min_sayi) and kontrol_fonksiyonu(kalan_taslar, min_sayi):
            return (list(grup1_kombinasyonu), kalan_taslar)
    return False

@logger.log_function
def karma_per_dogrula(taslar, min_sayi):
    if len(taslar) != min_sayi * 2: return False
    for kut_kombinasyonu in combinations(taslar, min_sayi):
        seri_taslar = [t for t in taslar if t not in kut_kombinasyonu]
        if kut_mu(list(kut_kombinasyonu), min_sayi) and seri_mu(seri_taslar, min_sayi):
            return (list(kut_kombinasyonu), seri_taslar)
    for seri_kombinasyonu in combinations(taslar, min_sayi):
        kut_taslar = [t for t in taslar if t not in seri_kombinasyonu]
        if seri_mu(list(seri_kombinasyonu), min_sayi) and kut_mu(kut_taslar, min_sayi):
            return (list(seri_kombinasyonu), kut_taslar)
    return False

@logger.log_function
def cift_per_mu(taslar):
    if len(taslar) < 8 or len(taslar) % 2 != 0: return False
    tas_gruplari, joker_sayisi = {}, 0
    for tas in taslar:
        if tas.renk == "joker": joker_sayisi += 1
        else:
            anahtar = (tas.renk, tas.deger)
            tas_gruplari[anahtar] = tas_gruplari.get(anahtar, 0) + 1
    tek_kalan_sayisi = sum(1 for sayi in tas_gruplari.values() if sayi % 2 != 0)
    return joker_sayisi >= tek_kalan_sayisi