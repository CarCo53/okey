# ai/ai_player.py
from core.player import Player
from itertools import combinations

from rules.rules_manager import Rules
from ai.strategies.planlama_stratejisi import eli_analiz_et
from ai.strategies.discard_stratejisi import en_akilli_ati_bul
from ai.strategies.cift_stratejisi import en_iyi_ciftleri_bul, atilacak_en_kotu_tas as atilacak_en_kotu_cift
from ai.strategies.coklu_per_stratejisi import en_iyi_coklu_per_bul
from ai.strategies.klasik_per_stratejisi import en_iyi_per_bul
from log import logger

class AIPlayer(Player):
    @logger.log_function
    def __init__(self, isim):
        super().__init__(isim)
        self.potansiyel_perler = []
        self.ihtiyac_listesi = {}

    @logger.log_function
    def _elini_yeniden_degerlendir(self, game):
        self.potansiyel_perler, self.ihtiyac_listesi = eli_analiz_et(self.el, game)
    
    @logger.log_function
    def atilan_tasi_degerlendir(self, oyun, atilan_tas):
        my_index = oyun.oyuncular.index(self)
        # Eğer elini açtıysa ve işleyebiliyorsa alsın
        if oyun.acilmis_oyuncular[my_index]:
            if self.ai_islem_yap_dene(oyun, ek_tas=atilan_tas):
                logger.info(f"AI {self.isim} masaya işleyebileceği için taşı alıyor: {atilan_tas}")
                return True
        
        # Eğer görev 'Çift' ise ve elinde o taşın eşi varsa alsın (YENİ KOD)
        if oyun.mevcut_gorev == "Çift":
            for tas in self.el:
                if tas.renk != "joker" and tas.renk == atilan_tas.renk and tas.deger == atilan_tas.deger:
                    logger.info(f"AI {self.isim} 'Çift' görevi için atılan taşı alıyor: {atilan_tas}")
                    return True

        # Normal perler için ihtiyacı varsa alsın (mevcut mantık)
        self._elini_yeniden_degerlendir(oyun)
        aranan_tas = (atilan_tas.renk, atilan_tas.deger)
        if aranan_tas in self.ihtiyac_listesi:
             logger.info(f"AI {self.isim} planı dahilindeki taşı alıyor: {atilan_tas}")
             return True

        return False
    
    @logger.log_function
    def ai_el_ac_dene(self, oyun):
        gorev = oyun.mevcut_gorev
        kombinasyon = None
        if "Çift" in gorev: kombinasyon = en_iyi_ciftleri_bul(self.el, gorev)
        elif "+" in gorev or "2x" in gorev: kombinasyon = en_iyi_coklu_per_bul(self.el, gorev)
        else: kombinasyon = en_iyi_per_bul(self.el, gorev)
        return [tas.id for tas in kombinasyon] if kombinasyon else None
    
    @logger.log_function
    def karar_ver_ve_at(self, oyun):
        my_index = oyun.oyuncular.index(self)
        if oyun.mevcut_gorev == "Çift" and not oyun.acilmis_oyuncular[my_index]:
            return atilacak_en_kotu_cift(self.el)
        self._elini_yeniden_degerlendir(oyun)
        korunacak_taslar_idler = {tas.id for per in self.potansiyel_perler for tas in per}
        if oyun.acilmis_oyuncular[my_index]:
            # El açtığı turda değilse işleyebileceği taşları koru
            if oyun.ilk_el_acan_tur.get(my_index, -1) < oyun.tur_numarasi:
                isleyebilecegim_hamleler = self.ai_islem_yap_dene(oyun, return_all_options=True)
                if isleyebilecegim_hamleler:
                    for hamle in isleyebilecegim_hamleler:
                        korunacak_taslar_idler.add(hamle["tas_id"])
        atilabilecekler = [t for t in self.el if t.id not in korunacak_taslar_idler]
        if not atilabilecekler: atilabilecekler = self.el
        return en_akilli_ati_bul(self.el, atilabilecekler)

    @logger.log_function
    def ai_islem_yap_dene(self, oyun, return_all_options=False, ek_tas=None):
        bulunan_hamleler = []
        gecici_el = self.el + ([ek_tas] if ek_tas else [])
        for tas in gecici_el:
            for sahip_idx, per_listesi in oyun.acilan_perler.items():
                for per_idx, per in enumerate(per_listesi):
                    for per_tasi in per:
                        if per_tasi.renk == "joker" and per_tasi.joker_yerine_gecen:
                            if (per_tasi.joker_yerine_gecen.renk == tas.renk and 
                                per_tasi.joker_yerine_gecen.deger == tas.deger):
                                hamle = {"sahip_idx": sahip_idx, "per_idx": per_idx, "tas_id": tas.id}
                                if not return_all_options: return hamle
                                bulunan_hamleler.append(hamle)
                    if Rules.islem_dogrula(per, tas):
                        hamle = {"sahip_idx": sahip_idx, "per_idx": per_idx, "tas_id": tas.id}
                        if not return_all_options: return hamle
                        bulunan_hamleler.append(hamle)
        return bulunan_hamleler if return_all_options else (bulunan_hamleler[0] if bulunan_hamleler else None)