# ai/strategies/planlama_stratejisi.py
from collections import Counter, defaultdict
from itertools import combinations
from log import logger
from rules.per_validators import kut_mu, seri_mu
from core.tile import Tile

@logger.log_function
def _get_oyundaki_taslar(perler):
    oyundaki_taslar = Counter()
    for per in perler:
        for tas in per:
            gercek_tas = tas.joker_yerine_gecen if tas.renk == 'joker' else tas
            if gercek_tas:
                oyundaki_taslar[(gercek_tas.tas_rengi, gercek_tas.deger)] += 1
    return oyundaki_taslar

@logger.log_function
def eli_analiz_et(el):
    el_analizi = {
        "ciftler": [],
        "uc_taslilar": [],
        "dort_taslilar": [],
        "seriler": [],
        "ikili_potansiyeller": {"seri": [], "kut": []}
    }
    
    # Grupları renge göre ayır
    renk_gruplari = defaultdict(list)
    for tas in el:
        if tas.renk != 'joker':
            renk_gruplari[tas.renk].append(tas)
    
    for renk in renk_gruplari:
        renk_gruplari[renk].sort(key=lambda t: t.deger)

    # Perleri bul (seri)
    for renk, tas_listesi in renk_gruplari.items():
        if len(tas_listesi) >= 3:
            for i in range(len(tas_listesi) - 2):
                if tas_listesi[i+1].deger == tas_listesi[i].deger + 1 and tas_listesi[i+2].deger == tas_listesi[i+1].deger + 1:
                    seri = [tas_listesi[i], tas_listesi[i+1], tas_listesi[i+2]]
                    el_analizi["seriler"].append(seri)
    
    # Perleri bul (küt ve çift)
    renk_deger_gruplari = defaultdict(list)
    deger_gruplari = defaultdict(list)
    for tas in el:
        if tas.renk != 'joker':
            anahtar = (tas.renk, tas.deger)
            renk_deger_gruplari[anahtar].append(tas)
            deger_gruplari[tas.deger].append(tas)
            
    for tas_listesi in renk_deger_gruplari.values():
        if len(tas_listesi) == 2:
             el_analizi["ciftler"].append(tas_listesi)
    
    for deger, tas_listesi in deger_gruplari.items():
        if len(tas_listesi) >= 3:
            # Sadece farklı renkteki taşları kontrol et
            renkler_seti = {t.renk for t in tas_listesi}
            if len(renkler_seti) >= 3:
                if len(tas_listesi) == 3:
                    el_analizi["uc_taslilar"].append(tas_listesi)
                elif len(tas_listesi) == 4:
                    el_analizi["dort_taslilar"].append(tas_listesi)

    # Potansiyel perleri bul (ikililer)
    for renk, tas_listesi in renk_gruplari.items():
        for i in range(len(tas_listesi) - 1):
            if tas_listesi[i+1].deger - tas_listesi[i].deger <= 2:
                el_analizi["ikili_potansiyeller"]["seri"].append((tas_listesi[i], tas_listesi[i+1]))
                
    for deger, tas_listesi in deger_gruplari.items():
        if len(tas_listesi) == 2:
            el_analizi["ikili_potansiyeller"]["kut"].append(tuple(tas_listesi))
            
    return el_analizi

@logger.log_function
def en_akilli_ati_bul(el, el_analizi, atilan_taslar):
    # Joker taşları asla atılmamalı
    jokersiz_el = [t for t in el if t.renk != "joker"]
    if not jokersiz_el:
        # El sadece jokerlerden oluşuyorsa en yüksek değerli olanı at
        return max(el, key=lambda t: t.deger)
        
    # En az faydalı taşı atma stratejisi
    en_kotu_tas = None
    
    # Önce alakasız tek taşları at
    tek_taslar = [t for t in jokersiz_el if t not in [item for sublist in el_analizi["uc_taslilar"] for item in sublist] and
                  t not in [item for sublist in el_analizi["dort_taslilar"] for item in sublist] and
                  t not in [item for sublist in el_analizi["seriler"] for item in sublist]]
    
    if tek_taslar:
        # En yüksek değerli alakasız taşı at
        en_kotu_tas = max(tek_taslar, key=lambda t: t.deger)
    
    # Alakasız taş yoksa, perleri bozma riskine göre at
    if en_kotu_tas is None:
        # Okey'e yakın, ancak bir per oluşturmayan taşları atma stratejisi
        for tas in jokersiz_el:
            if tas.deger != 1 and tas.deger != 13: # 1-13 döngüsüne ait olabilecek taşları koru
                 if not any(tas in per for per in el_analizi["seriler"]) and \
                    not any(tas in per for per in el_analizi["uc_taslilar"]) and \
                    not any(tas in per for per in el_analizi["dort_taslilar"]):
                         en_kotu_tas = tas
                         break
    
    # Hala bir taş bulamadıysa, en yüksek değerli alakasız taşı at
    if en_kotu_tas is None and jokersiz_el:
        en_kotu_tas = max(jokersiz_el, key=lambda t: t.deger)

    return en_kotu_tas