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
        # Eğer elini açtıysa ve işleyebiliyorsa veya jokeri değiştirebiliyorsa alsın
        if oyun.acilmis_oyuncular[my_index]:
            if self.ai_islem_yap_dene(oyun, ek_tas=atilan_tas):
                logger.info(f"AI {self.isim} masaya işleyebileceği için taşı alıyor: {atilan_tas}")
                return True
        
        # Eğer görev 'Çift' ise ve elinde o taşın eşi varsa alsın
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
        # Oyunun kuralına göre ilk açılışta göreve uygun perler aranır.
        if not oyun.acilmis_oyuncular[oyun.oyuncular.index(self)]:
            if "Çift" in gorev: kombinasyon = en_iyi_ciftleri_bul(self.el, gorev)
            elif "+" in gorev or "2x" in gorev: kombinasyon = en_iyi_coklu_per_bul(self.el, gorev)
            else: kombinasyon = en_iyi_per_bul(self.el, gorev)
        else: # El zaten açıksa, genel perler aranır.
            # Sadece tekli per açma stratejisi. Çoklu perler açılmıyor.
            kombinasyon = self.en_iyi_genel_per_bul()
        
        return [tas.id for tas in kombinasyon] if kombinasyon else None

    @logger.log_function
    def en_iyi_genel_per_bul(self):
        # Seri perleri ara
        for i in range(len(self.el), 2, -1):
            for combo in combinations(self.el, i):
                if Rules.genel_per_dogrula(list(combo)):
                    return list(combo)

        return None
    
    @logger.log_function
    def karar_ver_ve_at(self, oyun):
        my_index = oyun.oyuncular.index(self)
        okey_tasi = oyun.deste.okey_tasi()
        
        # Okey taşını atmaktan kaçın.
        if okey_tasi and okey_tasi in self.el and len(self.el) > 1:
            self.el.remove(okey_tasi)
            tas_to_discard = self.el.pop() # Herhangi bir taşı at.
            self.el.append(okey_tasi)
            return tas_to_discard

        # Eğer görev 'Çift' ise ve henüz elini açmadıysa
        if oyun.mevcut_gorev == "Çift" and not oyun.acilmis_oyuncular[my_index]:
            return atilacak_en_kotu_cift(self.el)

        # Diğer durumlar
        self._elini_yeniden_degerlendir(oyun)
        korunacak_taslar_idler = {tas.id for per in self.potansiyel_perler for tas in per}
        
        if oyun.acilmis_oyuncular[my_index]:
            # El açtığı turda değilse işleyebileceği taşları koru
            if oyun.ilk_el_acan_tur.get(my_index, -1) < oyun.tur_numarasi:
                islem_hamlesi = self.ai_islem_yap_dene(oyun)
                if islem_hamlesi:
                    korunacak_taslar_idler.add(islem_hamlesi["tas_id"])
        
        atilabilecekler = [t for t in self.el if t.id not in korunacak_taslar_idler]
        
        if not atilabilecekler:
            atilabilecekler = self.el
        
        return en_akilli_ati_bul(self.el, atilabilecekler)

    @logger.log_function
    def ai_islem_yap_dene(self, oyun, ek_tas=None):
        gecici_el = self.el + ([ek_tas] if ek_tas else [])
        
        # 1. Önce joker değiştirme hamlelerini kontrol et
        for tas in gecici_el:
            for sahip_idx, per_listesi in oyun.acilan_perler.items():
                for per_idx, per in enumerate(per_listesi):
                    for per_tasi in per:
                        if per_tasi.renk == "joker" and per_tasi.joker_yerine_gecen:
                            yerine_gecen = per_tasi.joker_yerine_gecen
                            if (yerine_gecen.renk == tas.renk and 
                                yerine_gecen.deger == tas.deger):
                                return {"action_type": "joker_degistir", "sahip_idx": sahip_idx, "per_idx": per_idx, "tas_id": tas.id}

        # 2. Ardından normal taş işleme hamlelerini kontrol et
        for tas in gecici_el:
            for sahip_idx, per_listesi in oyun.acilan_perler.items():
                for per_idx, per in enumerate(per_listesi):
                    if Rules.islem_dogrula(per, tas):
                        return {"action_type": "islem_yap", "sahip_idx": sahip_idx, "per_idx": per_idx, "tas_id": tas.id}
                        
        return None