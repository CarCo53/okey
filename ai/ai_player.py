# ai/ai_player.py

import random
from core.player import Player
from core.game_state import GameState
from rules.rules_manager import Rules
from rules.per_validators import seri_mu, kut_mu
from ai.strategies.planlama_stratejisi import eli_analiz_et, en_akilli_ati_bul
from ai.strategies.klasik_per_stratejisi import en_iyi_per_bul
from ai.strategies.coklu_per_stratejisi import en_iyi_coklu_per_bul
from log import logger

class AIPlayer(Player):
    @logger.log_function
    def __init__(self, isim, index):
        super().__init__(isim, index)
        self.oyun_analizi = None

    @logger.log_function
    def atilan_tasi_degerlendir(self, game, atilan_tas):
        # Elini açmış bir oyuncu için atılan taşı değerlendir
        if game.acilmis_oyuncular[self.index]:
            for per_idx, per in enumerate(game.acilan_perler[self.index]):
                if Rules.islem_dogrula(per, atilan_tas):
                    logger.info(f"AI {self.isim} açılmış perine taş eklemek için atılan taşı alıyor: {atilan_tas.renk}_{atilan_tas.deger}")
                    return True
        
        # Elini açmamış bir oyuncu için atılan taşı değerlendir
        else:
            # Atılan taşla yeni bir per oluşturulabiliyor mu?
            gecici_el = self.el + [atilan_tas]
            gecici_el_analizi = eli_analiz_et(gecici_el)
            
            # Göreve uygun bir per oluşturma potansiyeli var mı?
            if any(Rules.per_dogrula(list(kombo), game.mevcut_gorev) for kombo in gecici_el_analizi['seriler'] + gecici_el_analizi['uc_taslilar'] + gecici_el_analizi['dort_taslilar'] + gecici_el_analizi['ciftler']):
                logger.info(f"AI {self.isim} görevi tamamlamak için atılan taşı alıyor: {atilan_tas.renk}_{atilan_tas.deger}")
                return True
            
            # Elini açmamış olsa bile işine yarayan bir taşı alabilir.
            # Örneğin, bir ikiliyi üçlüye tamamlıyorsa veya bir seriyi uzatıyorsa.
            # Bu, AI'ın daha akıllıca kararlar vermesini sağlar.
            if any(atilan_tas in potansiyel for potansiyel in gecici_el_analizi['ikili_potansiyeller']['seri'] + gecici_el_analizi['ikili_potansiyeller']['kut']):
                logger.info(f"AI {self.isim} potansiyel per oluşturmak için atılan taşı alıyor: {atilan_tas.renk}_{atilan_tas.deger}")
                return True

        logger.info(f"AI {self.isim} atılan taşı değerlendiriyor. Almadı.")
        return False


    @logger.log_function
    def ai_el_ac_dene(self, game):
        """
        AI'nin elini açmak için en iyi per kombinasyonunu bulmaya çalışır.
        Brute-force yerine akıllı stratejiler kullanır.
        """
        # Önce eldeki potansiyel perleri analiz et
        el_analizi = eli_analiz_et(self.el)
        
        # Görevin ne olduğuna bağlı olarak farklı stratejiler uygula
        gorev = game.mevcut_gorev
        
        # İlk el açılışı için göreve özel per arama
        if not game.acilmis_oyuncular[self.index]:
            if gorev == "Çift":
                # Çift görevini kontrol et
                # Burada özel bir çift stratejisi fonksiyonu çağrılabilir.
                # Örnek: from ai.strategies.cift_stratejisi import en_iyi_ciftleri_bul
                # acilacak_per = en_iyi_ciftleri_bul(self.el, gorev)
                # Şimdilik planlama stratejisi içinde de bu mantık olabilir.
                return [t.id for t in el_analizi["ciftler"] if Rules.per_dogrula(el_analizi["ciftler"], gorev)]
            
            if "2x" in gorev or "+" in gorev:
                # Çoklu veya karma görevler için kombinasyonları dene
                # Bu kısım karmaşık olduğu için dış strateji fonksiyonu kullanılabilir.
                acilacak_per = en_iyi_coklu_per_bul(self.el, gorev)
                if acilacak_per:
                    return [t.id for t in acilacak_per]
            
            # Klasik per görevleri için
            acilacak_per = en_iyi_per_bul(self.el, gorev)
            if acilacak_per:
                return [t.id for t in acilacak_per]
        
        # Zaten eli açılmış oyuncu için genel per arama
        else:
            # Önce en iyi perleri bulmaya çalış
            # Seri perler
            for per in el_analizi["seriler"]:
                if Rules.genel_per_dogrula(per): return [t.id for t in per]
            # Küt perler
            for per in el_analizi["uc_taslilar"] + el_analizi["dort_taslilar"]:
                if Rules.genel_per_dogrula(per): return [t.id for t in per]
            
            # Potansiyel perleri bir araya getirmeye çalış (basit bir kombinasyon denemesi)
            aday_taslar = el_analizi["ikili_potansiyeller"]["seri"] + el_analizi["ikili_potansiyeller"]["kut"]
            for i in range(3, len(self.el) + 1):
                for kombo in combinations(self.el, i):
                    if Rules.genel_per_dogrula(list(kombo)):
                        return [t.id for t in kombo]
        
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