# ai/strategies/coklu_per_stratejisi.py

from itertools import combinations
from rules.rules_manager import Rules
from rules.per_validators import kut_mu, seri_mu
from log import logger

@logger.log_function
def en_iyi_coklu_per_bul(el, gorev):
    """
    Yapay zekanın elindeki taşlardan "2x Küt 3" veya "Küt 3 + Seri 3" gibi
    çoklu veya karma görevleri verimli bir şekilde bulmasını sağlar.
    """
    # --- Görevleri Ayrıştırma ---
    try:
        if "2x" in gorev:
            # "2x Küt 3" veya "2x Seri 3" gibi görevler
            parcalar = gorev.split(' ')
            tip_str = parcalar[1].lower()
            min_sayi = int(parcalar[2])
            toplam_tas_sayisi = min_sayi * 2
            
            if len(el) < toplam_tas_sayisi:
                return None

            kontrol_fonksiyonu = kut_mu if tip_str == "küt" else seri_mu
            
            # Eldeki tüm olası ilk per kombinasyonlarını dene
            for grup1_kombinasyonu in combinations(el, min_sayi):
                if kontrol_fonksiyonu(list(grup1_kombinasyonu), min_sayi):
                    # İlk per geçerliyse, kalan taşları bul
                    kalan_taslar = [t for t in el if t not in grup1_kombinasyonu]
                    if len(kalan_taslar) >= min_sayi:
                        # Kalan taşlar içinde ikinci bir per ara
                        for grup2_kombinasyonu in combinations(kalan_taslar, min_sayi):
                            if kontrol_fonksiyonu(list(grup2_kombinasyonu), min_sayi):
                                # Başarılı! İki per'i birleştir ve döndür.
                                return list(grup1_kombinasyonu) + list(grup2_kombinasyonu)

        elif "+" in gorev:
            # "Küt 3 + Seri 3" gibi görevler
            parcalar = gorev.split(' ')
            tip1_str = parcalar[0].lower()
            min_sayi1 = int(parcalar[1])
            tip2_str = parcalar[3].lower()
            min_sayi2 = int(parcalar[4])
            toplam_tas_sayisi = min_sayi1 + min_sayi2

            if len(el) < toplam_tas_sayisi:
                return None

            kontrol1 = kut_mu if tip1_str == "küt" else seri_mu
            kontrol2 = seri_mu if tip2_str == "seri" else kut_mu

            # Eldeki tüm olası ilk per kombinasyonlarını dene
            for grup1_kombinasyonu in combinations(el, min_sayi1):
                if kontrol1(list(grup1_kombinasyonu), min_sayi1):
                    # İlk per geçerliyse, kalan taşları bul
                    kalan_taslar = [t for t in el if t not in grup1_kombinasyonu]
                    if len(kalan_taslar) >= min_sayi2:
                        # Kalan taşlar içinde ikinci per'i ara
                        for grup2_kombinasyonu in combinations(kalan_taslar, min_sayi2):
                            if kontrol2(list(grup2_kombinasyonu), min_sayi2):
                                # Başarılı! İki per'i birleştir ve döndür.
                                return list(grup1_kombinasyonu) + list(grup2_kombinasyonu)
    
    except (ValueError, IndexError):
        # Görev ayrıştırılamazsa
        return None
            
    return None