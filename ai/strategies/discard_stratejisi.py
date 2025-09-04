from log import logger
# ai/strategies/discard_stratejisi.py
@logger.log_function
def en_akilli_ati_bul(el, atilabilecek_taslar):
    if not atilabilecek_taslar:
        return el[0] if el else None
    
    guvenli_liste = [t for t in atilabilecek_taslar if t.renk != 'joker']
    if not guvenli_liste:
        for t in atilabilecek_taslar:
            if t.renk == 'joker' and not t.joker_yerine_gecen:
                return t
        return atilabilecek_taslar[0]

    en_dusuk_puan = float('inf')
    en_kotu_tas = None
    for tas in guvenli_liste:
        puan = 0
        for diger_tas in el:
            if tas.id != diger_tas.id:
                if tas.deger == diger_tas.deger: puan += 10
                if tas.renk == diger_tas.renk:
                    fark = abs(tas.deger - diger_tas.deger)
                    if fark == 1: puan += 12
                    elif fark == 2: puan += 6
        if tas.deger in [1, 13]: puan -= 3
        if puan < en_dusuk_puan:
            en_dusuk_puan, en_kotu_tas = puan, tas
    return en_kotu_tas or guvenli_liste[0]