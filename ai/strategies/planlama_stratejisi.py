# ai/strategies/planlama_stratejisi.py
from collections import Counter
from log import logger

@logger.log_function
def _get_oyundaki_taslar(game):
    sayac = Counter()
    for per_listesi in game.acilan_perler.values():
        for per in per_listesi:
            for tas in per:
                gercek_tas = tas.joker_yerine_gecen or tas
                if gercek_tas.renk != 'joker':
                    sayac[(gercek_tas.renk, gercek_tas.deger)] += 1
    for tas in game.atilan_taslar:
         if tas.renk != 'joker':
            sayac[(tas.renk, tas.deger)] += 1
    return sayac

@logger.log_function
def eli_analiz_et(el, game):
    oyundaki_taslar = _get_oyundaki_taslar(game)
    potansiyel_perler = []
    ihtiyac_listesi = {}

    # Potansiyel Seriler
    renk_gruplari = {}
    for tas in el:
        if tas.renk != 'joker':
            renk_gruplari.setdefault(tas.renk, []).append(tas)

    for renk, taslar in renk_gruplari.items():
        if len(taslar) < 2: continue
        sirali_taslar = sorted(taslar, key=lambda t: t.deger)
        for i in range(len(sirali_taslar) - 1):
            t1, t2 = sirali_taslar[i], sirali_taslar[i+1]
            fark = t2.deger - t1.deger
            if fark in [1, 2]:
                potansiyel_perler.append([t1, t2])
                if fark == 1: # 5-6 -> 4 ve 7'ye bakar
                    if t1.deger > 1:
                        ihtiyac = (renk, t1.deger - 1)
                        if oyundaki_taslar[ihtiyac] < 2: ihtiyac_listesi[ihtiyac] = [t1, t2]
                    if t2.deger < 13:
                        ihtiyac = (renk, t2.deger + 1)
                        if oyundaki_taslar[ihtiyac] < 2: ihtiyac_listesi[ihtiyac] = [t1, t2]
                else: # 5-7 -> 6'ya bakar
                    ihtiyac = (renk, t1.deger + 1)
                    if oyundaki_taslar[ihtiyac] < 2: ihtiyac_listesi[ihtiyac] = [t1, t2]

    # Potansiyel Kütler
    deger_gruplari = {}
    for tas in el:
        if tas.renk != 'joker':
            deger_gruplari.setdefault(tas.deger, []).append(tas)
    
    for deger, taslar in deger_gruplari.items():
        if len(taslar) == 2:
            potansiyel_perler.append(taslar)
            mevcut_renkler = {t.renk for t in taslar}
            eksik_renkler = {"sari", "mavi", "siyah", "kirmizi"} - mevcut_renkler
            for renk in eksik_renkler:
                ihtiyac = (renk, deger)
                if oyundaki_taslar[ihtiyac] < 2: ihtiyac_listesi[ihtiyac] = taslar
    return potansiyel_perler, ihtiyac_listesi