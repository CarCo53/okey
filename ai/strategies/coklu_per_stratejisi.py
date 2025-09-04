# ai/strategies/coklu_per_stratejisi.py
from itertools import combinations
from rules.rules_manager import Rules
from log import logger

@logger.log_function
def en_iyi_coklu_per_bul(el, gorev):
    try:
        toplam_tas_sayisi = 0
        if "2x" in gorev:
            min_sayi = int(gorev.split(' ')[-1])
            toplam_tas_sayisi = min_sayi * 2
        elif "+" in gorev:
            parcalar = gorev.split(' ')
            min_sayi1 = int(parcalar[1])
            min_sayi2 = int(parcalar[4])
            toplam_tas_sayisi = min_sayi1 + min_sayi2
        else:
            return None
    except (ValueError, IndexError):
        return None

    if len(el) < toplam_tas_sayisi:
        return None

    for combo in combinations(el, toplam_tas_sayisi):
        per = list(combo)
        if Rules.per_dogrula(per, gorev):
            return per
            
    return None