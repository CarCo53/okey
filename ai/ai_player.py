# ai/ai_player.py

import random
from itertools import combinations
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
        # Mevcut elin analizini yap
        el_analizi = eli_analiz_et(self.el)
        gorev = game.mevcut_gorev

        if game.acilmis_oyuncular[self.index]:
            # Elini açmış bir oyuncu için, geçerli perler bulup aç.
            for perler_listesi in [el_analizi['seriler'], el_analizi['uc_taslilar'], el_analizi['dort_taslilar']]:
                for per in perler_listesi:
                    if Rules.genel_per_dogrula(per):
                        return [t.id for t in per]
            return None
        else:
            # Elini açmamış bir oyuncu için, göreve uygun bir per bul.
            # `gorevler.py` içinde tanımlanan görev listesine göre kontrol et.
            if gorev.startswith("Seri"):
                for seri in el_analizi['seriler']:
                    if Rules.per_dogrula(seri, gorev):
                        return [t.id for t in seri]
            elif gorev.startswith("Küt"):
                for kut in el_analizi['uc_taslilar'] + el_analizi['dort_taslilar']:
                    if Rules.per_dogrula(kut, gorev):
                        return [t.id for t in kut]
            elif "x" in gorev or "+" in gorev:
                # Çoklu ve karma perler için özel kontrol
                # Şu anki eli direkt olarak `per_dogrula`ya gönderelim.
                # Daha sonra geliştirilebilir.
                if Rules.per_dogrula(self.el, gorev):
                    return [t.id for t in self.el]
            elif gorev == "Çift":
                if Rules.per_dogrula(self.el, gorev):
                    return [t.id for t in self.el]
            return None

    @logger.log_function
    def ai_islem_yap_dene(self, game):
        if not game.acilmis_oyuncular[self.index]: return None

        # Joker değiştirme kontrolü
        for per_sahibi_idx, perler in game.acilan_perler.items():
            for per_idx, per in enumerate(perler):
                joker_tasi = next((t for t in per if t.renk == "joker" and t.joker_yerine_gecen), None)
                if joker_tasi:
                    yerine_gecen = joker_tasi.joker_yerine_gecen
                    eslesen_tas = next((t for t in self.el if t.renk == yerine_gecen.renk and t.deger == yerine_gecen.deger), None)
                    if eslesen_tas:
                        return {"action_type": "joker_degistir", "sahip_idx": per_sahibi_idx, "per_idx": per_idx, "tas_id": eslesen_tas.id}
        
        # Geliştirilmiş işleme kontrolü
        for per_sahibi_idx, perler in game.acilan_perler.items():
            for per_idx, per in enumerate(perler):
                # Tek bir taş işleme
                for tas in self.el:
                    if tas.renk == "joker":
                        continue
                    if Rules.islem_dogrula(per, tas):
                        return {"action_type": "islem_yap", "sahip_idx": per_sahibi_idx, "per_idx": per_idx, "tas_id": tas.id}
                
                # Birden fazla taşı seri perlere işleme
                gruplar = self._get_consecutive_groups(self.el)
                for grup in gruplar:
                    # Grubun ilk elemanını eklemeye çalış
                    if Rules.islem_dogrula(per, grup[0]):
                        # Grup per'e eklenince geçerli bir per mi oluyor kontrol et
                        if seri_mu(per + list(grup)):
                            return {"action_type": "islem_yap", "sahip_idx": per_sahibi_idx, "per_idx": per_idx, "tas_id": [t.id for t in grup]}
                    
                    # Grubun son elemanını eklemeye çalış
                    if Rules.islem_dogrula(per, grup[-1]):
                         if seri_mu(per + list(grup)):
                            return {"action_type": "islem_yap", "sahip_idx": per_sahibi_idx, "per_idx": per_idx, "tas_id": [t.id for t in grup]}

        return None
    
    def _get_consecutive_groups(self, el):
        # Elindeki taşları renge göre gruplayıp, peş peşe gelenleri bulur
        renk_gruplari = {}
        for tas in el:
            if tas.renk not in renk_gruplari:
                renk_gruplari[tas.renk] = []
            renk_gruplari[tas.renk].append(tas)
        
        tum_gruplar = []
        for renk in renk_gruplari:
            renk_gruplari[renk].sort(key=lambda t: t.deger)
            if len(renk_gruplari[renk]) >= 2:
                grup = [renk_gruplari[renk][0]]
                for i in range(1, len(renk_gruplari[renk])):
                    if renk_gruplari[renk][i].deger == renk_gruplari[renk][i-1].deger + 1:
                        grup.append(renk_gruplari[renk][i])
                    else:
                        if len(grup) >= 2:
                            tum_gruplar.append(grup)
                        grup = [renk_gruplari[renk][i]]
                if len(grup) >= 2:
                    tum_gruplar.append(grup)
        return tum_gruplar

    @logger.log_function
    def karar_ver_ve_at(self, game):
        if not self.el: return None
        self.oyun_analizi = eli_analiz_et(self.el)
        atilan_tas = en_akilli_ati_bul(self.el, self.oyun_analizi, game.atilan_taslar)
        return atilan_tas
    
    def _el_acma_kombinasyonlari_uret(self):
        # Bu fonksiyon, AI'nin elindeki taşlarla olası per kombinasyonlarını üretir.
        # Yeni mantıkla doğrudan eli_analiz_et kullanıldığı için bu fonksiyona gerek kalmadı.
        return []