# rules/rules_manager.py
from rules.gorevler import GOREV_LISTESI
from rules.per_validators import kut_mu, seri_mu, coklu_per_dogrula, karma_per_dogrula, cift_per_mu
from core.tile import Tile
from log import logger

class Rules:
    GOREVLER = GOREV_LISTESI
    @staticmethod
    def per_dogrula(taslar, gorev):
        if gorev == "Küt 3": return len(taslar) == 3 and kut_mu(taslar, 3)
        if gorev == "Seri 3": return len(taslar) == 3 and seri_mu(taslar, 3)
        if gorev == "Küt 4": return len(taslar) == 4 and kut_mu(taslar, 4)
        if gorev == "Seri 4": return len(taslar) == 4 and seri_mu(taslar, 4)
        if gorev == "Seri 5": return len(taslar) == 5 and seri_mu(taslar, 5)
        if gorev == "2x Küt 3": return len(taslar) == 6 and coklu_per_dogrula(taslar, "küt", 3, 2)
        if gorev == "2x Seri 3": return len(taslar) == 6 and coklu_per_dogrula(taslar, "seri", 3, 2)
        if gorev == "Küt 3 + Seri 3": return len(taslar) == 6 and karma_per_dogrula(taslar, 3)
        if gorev == "2x Küt 4": return len(taslar) == 8 and coklu_per_dogrula(taslar, "küt", 4, 2)
        if gorev == "2x Seri 4": return len(taslar) == 8 and coklu_per_dogrula(taslar, "seri", 4, 2)
        if gorev == "Küt 4 + Seri 4": return len(taslar) == 8 and karma_per_dogrula(taslar, 4)
        if gorev == "Çift": return cift_per_mu(taslar)
        return False

    @staticmethod
    @logger.log_function
    def genel_per_dogrula(taslar):
        if len(taslar) < 3: return False
        return kut_mu(taslar, len(taslar)) or seri_mu(taslar, len(taslar))

    @staticmethod
    @logger.log_function
    def islem_dogrula(per, tas):
        if not per or not tas: return False
        if Rules._per_seri_mu(per): return Rules._seri_islem_dogrula(per, tas)
        elif Rules._per_kut_mu(per): return Rules._kut_islem_dogrula(per, tas)
        return False

    @staticmethod
    @logger.log_function
    def _per_kut_mu(per):
        degerler = {t.deger for t in per if t.joker_yerine_gecen or t.renk != "joker"}
        return len(degerler) <= 1

    @staticmethod
    @logger.log_function
    def _per_seri_mu(per):
        renkler = {t.renk for t in per if t.joker_yerine_gecen or t.renk != "joker"}
        return len(renkler) <= 1
        
    @staticmethod
    @logger.log_function
    def _kut_islem_dogrula(per, tas):
        if len(per) >= 4: return False
        per_degeri = next((t.deger for t in per if t.renk != "joker"), None)
        per_renkleri = {t.renk for t in per if t.renk != "joker"}
        if tas.renk == "joker": return True
        return tas.deger == per_degeri and tas.renk not in per_renkleri

    @staticmethod
    @logger.log_function
    def _seri_islem_dogrula(per, tas):
        per_rengi = next((t.renk for t in per if t.renk != "joker"), None)
        sayilar = sorted([t.deger for t in per if t.renk != "joker"])
        
        if tas.renk == "joker": return True
        if per_rengi and tas.renk != per_rengi: return False
        if not sayilar: return True

        en_kucuk = sayilar[0]
        en_buyuk = sayilar[-1]

        # Seriye eklenebilecek taşlar
        if tas.deger == en_kucuk - 1 or tas.deger == en_buyuk + 1:
            return True
        
        # Döngüsel serinin başına veya sonuna ekleme
        if en_kucuk == 1 and en_buyuk == 13:
            # 13-1 serisine 12 eklemek
            if len(sayilar) == 2 and sayilar == [1, 13] and tas.deger == 12:
                return True
        elif en_kucuk == 1 and tas.deger == 13:
             return True
        elif en_buyuk == 13 and tas.deger == 1:
            return True
            
        return False