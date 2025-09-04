# ai/strategies/cift_stratejisi.py
from collections import defaultdict
from rules.per_validators import cift_per_mu
from log import logger

@logger.log_function
def en_iyi_ciftleri_bul(el, gorev):
    if gorev != "Çift": return None
    jokerler = [t for t in el if t.renk == 'joker']
    ciftler, tekler = _ciftleri_ve_tekleri_bul(el)
    
    # Elimizdeki gerçek çiftler + jokerlerle oluşturulabilecek çift sayısı
    potansiyel_cift_sayisi = len(ciftler) + len(jokerler) // 2
    if potansiyel_cift_sayisi >= 4:
        acilacak_taslar = []
        for cift_grup in ciftler: acilacak_taslar.extend(cift_grup)
        
        kullanilacak_joker = 0
        if len(ciftler) < 4:
            eksik_cift = 4 - len(ciftler)
            # Her eksik çift için 1 tek taş ve 1 joker gerekir. Ama jokerler de çift oluşturabilir.
            # Şimdilik basit mantık: ne kadar tek varsa o kadar joker kullan.
            kullanilacak_joker = min(len(tekler), len(jokerler))

        acilacak_taslar.extend(jokerler[:kullanilacak_joker])
        acilacak_taslar.extend(tekler[:kullanilacak_joker])

        kalan_jokerler = jokerler[kullanilacak_joker:]
        acilacak_taslar.extend(kalan_jokerler[:(len(kalan_jokerler)//2)*2])

        if len(acilacak_taslar) >= 8 and cift_per_mu(acilacak_taslar):
            return acilacak_taslar[:8] # Görev için sadece 8 taş (4 çift) aç
            
    return None

@logger.log_function
def atilacak_en_kotu_tas(el):
    _ , tekler = _ciftleri_ve_tekleri_bul(el)
    joker_olmayan_tekler = [t for t in tekler if t.renk != 'joker']
    if joker_olmayan_tekler:
        return max(joker_olmayan_tekler, key=lambda t: t.deger or 0)
    
    # Atacak tek taş yoksa, en değersiz çifti boz
    ciftler, _ = _ciftleri_ve_tekleri_bul(el)
    if ciftler:
        en_dusuk_degerli_cift = min(ciftler, key=lambda c: c[0].deger)
        return en_dusuk_degerli_cift[0]
            
    return el[0] if el else None

@logger.log_function
def _ciftleri_ve_tekleri_bul(el):
    tas_gruplari = defaultdict(list)
    jokerler = [t for t in el if t.renk == 'joker']
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