# engine/game_manager.py

from core.deck import Deck
from core.player import Player
from ai.ai_player import AIPlayer
from core.game_state import GameState
from baslat import baslat_oyun
from rules.rules_manager import Rules
from engine.action_manager import ActionManager
from engine.turn_manager import TurnManager
from log import logger

class Game:
    @logger.log_function
    def __init__(self):
        self.oyuncular = [Player("Oyuncu 1 (Siz)", 0), AIPlayer("AI Oyuncu 2", 1), AIPlayer("AI Oyuncu 3", 2), AIPlayer("AI Oyuncu 4", 3)]
        self.deste = Deck()
        self.atilan_taslar = []
        self.sira_kimde_index = 0
        self.oyun_durumu = GameState.NORMAL_TUR
        self.acilan_perler = {i: [] for i in range(len(self.oyuncular))}
        self.turda_tas_cekildi = [False] * len(self.oyuncular)
        self.atilan_tas_degerlendirici = None
        self.acilmis_oyuncular = [False] * len(self.oyuncular)
        self.mevcut_gorev = None
        self.kazanan_index = None
        self.tur_numarasi = 1
        self.ilk_el_acan_tur = {}
        self.arayuz = None
        self.oyuncu_hamle_yapti = [False] * len(self.oyuncular)
        self.game_over = False

    @logger.log_function
    def baslat(self, gorev=None):
        baslat_oyun(self, gorev)
    
    @logger.log_function
    def el_ac(self, oyuncu_index, tas_id_list):
        result = ActionManager.el_ac(self, oyuncu_index, tas_id_list)
        if result and len(self.oyuncular[oyuncu_index].el) == 0:
            self.oyunu_bitir(oyuncu_index)
        return result

    @logger.log_function
    def islem_yap(self, isleyen_oyuncu_idx, per_sahibi_idx, per_idx, tas_id):
        result = ActionManager.islem_yap(self, isleyen_oyuncu_idx, per_sahibi_idx, per_idx, tas_id)
        if result and len(self.oyuncular[isleyen_oyuncu_idx].el) == 0:
            self.oyunu_bitir(isleyen_oyuncu_idx)
        return result
        
    @logger.log_function
    def joker_degistir(self, degistiren_oyuncu_idx, per_sahibi_idx, per_idx, tas_id):
        return ActionManager.joker_degistir(self, degistiren_oyuncu_idx, per_sahibi_idx, per_idx, tas_id)

    @logger.log_function
    def tas_at(self, oyuncu_index, tas_id):
        result = TurnManager.tas_at(self, oyuncu_index, tas_id)
        if not self.deste.taslar:
             self.oyunu_bitir(kazanan_index=None)
        return result

    @logger.log_function
    def desteden_cek(self, oyuncu_index):
        if not self.deste.taslar:
            self.oyunu_bitir(kazanan_index=None)
            return False
        return TurnManager.desteden_cek(self, oyuncu_index)

    @logger.log_function
    def atilan_tasi_al(self, oyuncu_index):
        if not self.deste.taslar:
            self.oyunu_bitir(kazanan_index=None)
            return False
        return TurnManager.atilan_tasi_al(self, oyuncu_index)

    @logger.log_function
    def atilan_tasi_gecti(self):
        return TurnManager.atilan_tasi_gecti(self)

    @logger.log_function
    def el_ac_joker_ile(self, oyuncu_index, secilen_taslar, joker, secilen_deger):
        joker.joker_yerine_gecen = secilen_deger
        return ActionManager._eli_ac_ve_isle(self, oyuncu_index, secilen_taslar)

    @logger.log_function
    def _sira_ilerlet(self, yeni_index):
        if yeni_index < self.sira_kimde_index:
            self.tur_numarasi += 1
            logger.info(f"Yeni tura geçildi: Tur {self.tur_numarasi}")
        self.sira_kimde_index = yeni_index
        self.oyuncu_hamle_yapti = [False] * len(self.oyuncular)
        
    @logger.log_function
    def _per_sirala(self, per):
        if not per: return
        is_seri = Rules._per_seri_mu(per)
        if not is_seri:
            per.sort(key=lambda t: (t.joker_yerine_gecen or t).deger or 0)
        else:
            sayilar = sorted([(t.joker_yerine_gecen or t).deger for t in per if t.joker_yerine_gecen or t.renk != 'joker'])
            if 1 in sayilar and 13 in sayilar:
                per.sort(key=lambda t: 14 if (t.joker_yerine_gecen or t).deger == 1 else (t.joker_yerine_gecen or t).deger or 0)
            else:
                per.sort(key=lambda t: (t.joker_yerine_gecen or t).deger or 0)
    
    @logger.log_function
    def oyunu_bitir(self, kazanan_index):
        self.oyun_durumu = GameState.BITIS
        self.kazanan_index = kazanan_index
        self.game_over = True
        logger.info(f"Oyun Bitti. Kazanan: {self.oyuncular[kazanan_index].isim}" if kazanan_index is not None else "Oyun Bitti. Deste Tükendi.")

    def oyun_bitti_mi(self):
        return self.game_over or not self.deste.taslar