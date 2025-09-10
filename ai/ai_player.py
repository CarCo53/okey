# ai/ai_player.py

import random
from core.player import Player
from core.game_state import GameState
from rules.rules_manager import Rules
from rules.per_validators import seri_mu, kut_mu
from ai.strategies.planlama_stratejisi import eli_analiz_et, en_akilli_ati_bul
from log import logger

class AIPlayer(Player):
    @logger.log_function
    def __init__(self, isim, index):
        super().__init__(isim, index)
        self.oyun_analizi = None

    @logger.log_function
    def atilan_tasi_degerlendir(self, game, atilan_tas):
        self.oyun_analizi = eli_analiz_et(self.el)
        
        # Kendi elini açmış bir oyuncu için, işine yarayan her taşı al
        if game.acilmis_oyuncular[self.index]:
            perler = game.acilan_perler[self.index]
            for per_idx, per in enumerate(perler):
                if Rules.islem_dogrula(per, atilan_tas):
                    logger.info(f"AI {self.index} planı dahilindeki taşı alıyor: {atilan_tas}")
                    return True

        # Elini açmamış bir oyuncu için strateji:
        # 1. Eğer per yapma potansiyeli varsa
        for per_tipi, per_listesi in self.oyun_analizi.get('ikili_potansiyeller', {}).items():
            for potansiyel_per in per_listesi:
                if atilan_tas in potansiyel_per:
                    logger.info(f"AI {self.index} per yapma potansiyeli için taşı alıyor: {atilan_tas}")
                    return True
        
        logger.info(f"AI {self.index} atılan taşı değerlendiriyor. Almadı.")
        return False

    @logger.log_function
    def ai_el_ac_dene(self, game):
        if game.acilmis_oyuncular[self.index]:
            # El zaten açıksa, yeni bir per açmayı dener
            kombinasyonlar = self._el_acma_kombinasyonlari_uret()
            for kombo in kombinasyonlar:
                if Rules.genel_per_dogrula(kombo):
                    return [t.id for t in kombo]
            return None
        else:
            # El henüz açılmadıysa, göreve uygun bir per açmayı dener
            gorev = game.mevcut_gorev
            for tas_ids in self._el_acma_kombinasyonlari_uret():
                if Rules.per_dogrula([t for t in self.el if t.id in tas_ids], gorev):
                    return tas_ids
            return None

    @logger.log_function
    def ai_islem_yap_dene(self, game):
        if not game.acilmis_oyuncular[self.index]: return None
        if game.ilk_el_acan_tur.get(self.index, -1) >= game.tur_numarasi: return None

        # Joker değiştirme kontrolü
        for per_sahibi_idx, perler in game.acilan_perler.items():
            for per_idx, per in enumerate(perler):
                joker_tasi = next((t for t in per if t.renk == "joker" and t.joker_yerine_gecen), None)
                if joker_tasi:
                    yerine_gecen = joker_tasi.joker_yerine_gecen
                    eslesen_tas = next((t for t in self.el if t.renk == yerine_gecen.renk and t.deger == yerine_gecen.deger), None)
                    if eslesen_tas:
                        return {"action_type": "joker_degistir", "sahip_idx": per_sahibi_idx, "per_idx": per_idx, "tas_id": eslesen_tas.id}
        
        # Normal işleme kontrolü
        for tas in self.el:
            for per_sahibi_idx, perler in game.acilan_perler.items():
                for per_idx, per in enumerate(perler):
                    if Rules.islem_dogrula(per, tas):
                        return {"action_type": "islem_yap", "sahip_idx": per_sahibi_idx, "per_idx": per_idx, "tas_id": tas.id}
        
        return None

    @logger.log_function
    def karar_ver_ve_at(self, game):
        if not self.el: return None
        self.oyun_analizi = eli_analiz_et(self.el)
        atilan_tas = en_akilli_ati_bul(self.el, self.oyun_analizi, game.atilan_taslar)
        return atilan_tas

    def _el_acma_kombinasyonlari_uret(self):
        # Bu fonksiyon, AI'nin elindeki taşlarla olası per kombinasyonlarını üretir.
        # Basit bir örnek olarak, 3'lü ve 4'lü tüm kombinasyonları döndürür.
        from itertools import combinations
        kombinasyonlar = []
        for i in range(3, len(self.el) + 1):
            kombinasyonlar.extend(list(combinations(self.el, i)))
        return kombinasyonlar