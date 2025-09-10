# ai/strategies/klasik_per_stratejisi.py

from itertools import combinations
from rules.rules_manager import Rules
from collections import defaultdict

def en_iyi_per_bul(el, gorev):
    """
    Yapay zekanın elindeki taşlardan görevle uyumlu en iyi (en çok taş içeren)
    klasik per'i (seri veya küt) verimli bir şekilde bulur.
    """
    bulunan_perler = []
    
    # Elimizdeki jokerleri ve normal taşları ayıralım
    jokerler = [t for t in el if t.renk == 'joker']
    normal_taslar = [t for t in el if t.renk != 'joker']

    # Olası tüm perleri bulmak için bir kombinasyon listesi oluşturalım.
    # Bu, eldeki taş sayısına göre arama boyutunu sınırlar.
    aranacak_boyutlar = sorted(list(set(range(3, len(el) + 1))), reverse=True)

    for boyut in aranacak_boyutlar:
        # Elimizdeki taşlardan ilgili boyutta kombinasyonlar deneriz.
        for combo in combinations(el, boyut):
            per = list(combo)
            # Eğer bu kombinasyon görev için geçerli bir per ise,
            # daha fazla aramaya gerek yok, çünkü en büyükten başladık.
            if Rules.per_dogrula(per, gorev):
                return per
            
    return None