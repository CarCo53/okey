# ai/strategies/degerlendirme_stratejisi.py
from ai.strategies.discard_stratejisi import en_akilli_ati_bul
from log import logger

@logger.log_function
def _eli_puanla(el):
    if not el: return 0
    puan = len([t for t in el if t.renk == 'joker']) * 25
    for tas in el:
        if tas.renk == 'joker': continue
        for diger_tas in el:
            if tas.id != diger_tas.id:
                if tas.deger == diger_tas.deger: puan += 10
                if tas.renk == diger_tas.renk:
                    fark = abs(tas.deger - diger_tas.deger)
                    if fark == 1: puan += 12
                    elif fark == 2: puan += 6
    return puan

@logger.log_function
def atilan_tasi_almaya_deger_mi(mevcut_el, atilan_tas, gorev_tamamlaniyor_mu):
    if gorev_tamamlaniyor_mu: return True
    mevcut_puan = _eli_puanla(mevcut_el)
    olasi_el = mevcut_el + [atilan_tas]
    yeni_puan = _eli_puanla(olasi_el)
    fayda = yeni_puan - mevcut_puan
    
    atilabilecekler = [t for t in olasi_el if t.id != atilan_tas.id]
    atılacak_tas = en_akilli_ati_bul(olasi_el, atilabilecekler)
    if not atılacak_tas: return False

    el_den_sonra = [t for t in olasi_el if t.id != atılacak_tas.id]
    son_puan = _eli_puanla(el_den_sonra)
    
    net_kazanc = son_puan - mevcut_puan
    return net_kazanc > 20