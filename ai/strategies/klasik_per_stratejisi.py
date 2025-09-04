# ai/strategies/klasik_per_stratejisi.py
from itertools import combinations
from rules.rules_manager import Rules
from log import logger

@logger.log_function
def en_iyi_per_bul(el, gorev):
    bulunan_perler = []
    for combo_size in range(3, len(el) + 1):
        for combo in combinations(el, combo_size):
            per = list(combo)
            if Rules.per_dogrula(per, gorev):
                bulunan_perler.append(per)
    return max(bulunan_perler, key=len) if bulunan_perler else None