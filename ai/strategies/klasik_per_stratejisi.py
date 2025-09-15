# ai/strategies/klasik_per_stratejisi.py

from itertools import combinations
from rules.rules_manager import Rules
from collections import defaultdict
from log import logger

@logger.log_function
def en_iyi_per_bul(el, gorev):
    """
    Yapay zekanın elindeki taşlardan görevle uyumlu en iyi (en çok taş içeren)
    klasik per'i (seri veya küt) verimli bir şekilde bulur.
    """
    gorev_tipi, min_sayi = gorev.split(' ') if ' ' in gorev else (gorev, 0)
    min_sayi = int(min_sayi) if min_sayi else 0
    
    jokerler = [t for t in el if t.renk == 'joker']
    normal_taslar = [t for t in el if t.renk != 'joker']
    
    if "Seri" in gorev:
        # Taşları renklere göre gruplandır
        renk_gruplari = defaultdict(list)
        for tas in normal_taslar:
            renk_gruplari[tas.renk].append(tas)
        
        for renk in renk_gruplari:
            tas_listesi = sorted(renk_gruplari[renk], key=lambda t: t.deger)
            benzersiz_degerler = sorted(list(set(t.deger for t in tas_listesi)))
            
            # En uzun seriden başla
            for i in range(len(benzersiz_degerler) - min_sayi + 1):
                for j in range(i + min_sayi - 1, len(benzersiz_degerler)):
                    aday_degerler = benzersiz_degerler[i:j+1]
                    # Boşluk sayısını hesapla
                    bosluk = (aday_degerler[-1] - aday_degerler[0] + 1) - len(aday_degerler)
                    if bosluk <= len(jokerler):
                        # Aday taşları ve jokerleri topla
                        aday_per = [t for t in tas_listesi if t.deger in aday_degerler] + jokerler[:bosluk]
                        if Rules.per_dogrula(aday_per, gorev):
                            return aday_per
    
    elif "Küt" in gorev:
        # Taşları değere göre gruplandır
        deger_gruplari = defaultdict(list)
        for tas in normal_taslar:
            deger_gruplari[tas.deger].append(tas)

        for deger in deger_gruplari:
            if len(deger_gruplari[deger]) + len(jokerler) >= min_sayi:
                aday_per = deger_gruplari[deger] + jokerler[:min_sayi - len(deger_gruplari[deger])]
                if Rules.per_dogrula(aday_per, gorev):
                    return aday_per
    
    elif gorev == "Çift":
        # Çift görevi için özel mantık
        from ai.strategies.cift_stratejisi import en_iyi_ciftleri_bul
        acilacak_per = en_iyi_ciftleri_bul(el, gorev)
        if acilacak_per:
            return acilacak_per

    # Eğer yukarıdaki yöntemlerle bulunamazsa, jokerlerle birlikte brute-force denemesi
    for boyut in range(min_sayi, len(el) + 1):
        for kombo in combinations(el, boyut):
            if Rules.per_dogrula(list(kombo), gorev):
                return list(kombo)
    
    return None