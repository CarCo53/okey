# ai/strategies/cift_stratejisi.py
from collections import defaultdict
from rules.per_validators import cift_per_mu
from log import logger
from core.tile import Tile

@logger.log_function
def en_iyi_ciftleri_bul(el, gorev):
    if gorev != "Çift":
        return None
    
    jokerler = [t for t in el if t.renk == 'joker']
    ciftler, tekler = _ciftleri_ve_tekleri_bul(el)

    # Elimizdeki toplam çift sayısını hesapla
    potansiyel_cift_sayisi = len(ciftler) + len(jokerler) // 2
    
    if potansiyel_cift_sayisi >= 4:
        acilacak_taslar = []
        
        # Gerçek çiftleri ekle
        for cift_grup in ciftler:
            acilacak_taslar.extend(cift_grup)

        # Eksik çiftleri joker ve tek taşlarla tamamla
        for i in range(min(len(tekler), len(jokerler))):
            acilacak_taslar.append(tekler[i])
            jokerler[i].joker_yerine_gecen = tekler[i]
            acilacak_taslar.append(jokerler[i])
            
        # Kalan jokerlerle çift oluştur
        kalan_jokerler = jokerler[min(len(tekler), len(jokerler)):]
        if len(kalan_jokerler) >= 2:
            acilacak_taslar.extend(kalan_jokerler)

        if cift_per_mu(acilacak_taslar):
            return acilacak_taslar
            
    return None

@logger.log_function
def atilacak_en_kotu_tas(el):
    _ , tekler = _ciftleri_ve_tekleri_bul(el)
    joker_olmayan_tekler = [t for t in tekler if t.renk != 'joker']
    if joker_olmayan_tekler:
        return max(joker_olmayan_tekler, key=lambda t: t.deger or 0)
    
    ciftler, _ = _ciftleri_ve_tekleri_bul(el)
    if ciftler:
        en_dusuk_degerli_cift = min(ciftler, key=lambda c: c[0].deger)
        return en_dusuk_degerli_cift[0]
            
    return el[0] if el else None

@logger.log_function
def _ciftleri_ve_tekleri_bul(el):
    tas_gruplari = defaultdict(list)
    for tas in el:
        if tas.renk != 'joker':
            anahtar = (tas.renk, tas.deger)
            tas_gruplari[anahtar].append(tas)
            
    ciftler, tekler = [], []
    for tas_listesi in tas_gruplari.values():
        cift_sayisi = len(tas_listesi) // 2
        for i in range(cift_sayisi):
            ciftler.append(tas_listesi[i*2 : i*2+2])
        if len(tas_listesi) % 2 != 0:
            tekler.append(tas_listesi[-1])
            
    return ciftler, tekler

@logger.log_function
def tasi_cift_yapar_mi(el, tas):
    """Verilen taşın, eldeki teklerden birini çifte dönüştürüp dönüştürmediğini kontrol eder."""
    _, tekler = _ciftleri_ve_tekleri_bul(el)
    for tek_tas in tekler:
        if tek_tas.renk == tas.renk and tek_tas.deger == tas.deger:
            return True
    return False