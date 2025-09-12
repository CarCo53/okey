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
        if len(per) >= 14: return False
        
        per_tasi_listesi = [t for t in per if t.renk != "joker"]
        if not per_tasi_listesi:
            if tas.renk == "joker": return True
            return False

        per_rengi = per_tasi_listesi[0].renk
        
        # Taşın rengi perle aynı mı?
        if tas.renk != "joker" and tas.renk != per_rengi: return False

        # Perdeki sayıları al, jokerlerin yerine geçen taşları da dahil et.
        sayilar = sorted([t.joker_yerine_gecen.deger if t.renk == "joker" else t.deger for t in per])
        sayilar_set = set(sayilar)
        
        tas_degeri = tas.deger
        
        # Eğer taş 1 ise ve seri döngüsel olabilirse, 14 olarak kabul edilir.
        if tas_degeri == 1 and 13 in sayilar_set and tas.renk == per_rengi:
             return True
        # Eğer taş 13 ise ve seri döngüsel olabilirse, 0 olarak kabul edilir.
        if tas_degeri == 13 and 1 in sayilar_set and tas.renk == per_rengi:
             return True

        # Normal seriye ekleme kuralları
        if tas_degeri == sayilar[0] - 1 or tas_degeri == sayilar[-1] + 1:
            return True
        
        # Kılavuzda belirtilen özel kurallar
        # Kural 1: 1-2-3 serisi mevcutken 13 eklenemez.
        if {1, 2, 3}.issubset(sayilar_set) and tas_degeri == 13:
             return False
        # Kural 2: 12-13-1 serisi mevcutken 2 eklenemez.
        if {12, 13, 1}.issubset(sayilar_set) and tas_degeri == 2:
            return False

        # Döngüsel seri durumunda 1'in 13'e eklenebilmesi
        if 13 in sayilar_set and tas_degeri == 1 and len(per) < 14 and per_rengi == tas.renk:
            return True
        
        # Döngüsel seri durumunda 2'nin 1'e eklenebilmesi (12-13-1 serisi için)
        if 1 in sayilar_set and 13 in sayilar_set and tas_degeri == 2 and len(per) < 14 and per_rengi == tas.renk:
            return True
        
        return False