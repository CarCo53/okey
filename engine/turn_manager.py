# engine/turn_manager.py
from core.game_state import GameState, AtilanTasDegerlendirici
from log import logger

class TurnManager:
    @staticmethod
    def tas_at(game, oyuncu_index, tas_id):
        oyuncu = game.oyuncular[oyuncu_index]
        if not oyuncu.el and game.acilmis_oyuncular[oyuncu_index]:
             game.oyun_durumu = GameState.BITIS
             game.kazanan_index = oyuncu_index
             return True
        if game.oyun_durumu not in [GameState.ILK_TUR, GameState.NORMAL_TAS_ATMA]:
            return False
        if oyuncu_index != game.sira_kimde_index:
            return False
        atilan_tas = oyuncu.tas_at(tas_id)
        if atilan_tas:
            game.atilan_taslar.append(atilan_tas)
            if game.acilmis_oyuncular[oyuncu_index] and not oyuncu.el:
                game.oyun_durumu = GameState.BITIS
                game.kazanan_index = oyuncu_index
                return True
            game.oyun_durumu = GameState.ATILAN_TAS_DEGERLENDIRME
            game.atilan_tas_degerlendirici = AtilanTasDegerlendirici(oyuncu_index, len(game.oyuncular))
            game.turda_tas_cekildi[oyuncu_index] = False
            return True
        return False

    @staticmethod
    def desteden_cek(game, oyuncu_index):
        if not (game.oyun_durumu == GameState.NORMAL_TUR and game.sira_kimde_index == oyuncu_index): return False
        oyuncu = game.oyuncular[oyuncu_index]
        tas = game.deste.tas_cek()
        if tas:
            oyuncu.tas_al(tas)
            game.turda_tas_cekildi[oyuncu_index] = True
            game.oyun_durumu = GameState.NORMAL_TAS_ATMA
            oyuncu.el_sirala()
            return True
        return False

    @staticmethod
    def atilan_tasi_al(game, oyuncu_index):
        if game.oyun_durumu != GameState.ATILAN_TAS_DEGERLENDIRME: return
        if not game.atilan_taslar: return
        alici_oyuncu = game.oyuncular[oyuncu_index]
        atilan_tas = game.atilan_taslar.pop()
        alici_oyuncu.tas_al(atilan_tas)
        game.turda_tas_cekildi[oyuncu_index] = True
        asil_sira_index = game.atilan_tas_degerlendirici.asilin_sirasi()
        if oyuncu_index == asil_sira_index:
            game._sira_ilerlet(oyuncu_index)
            game.oyun_durumu = GameState.NORMAL_TAS_ATMA
        else:
            ceza_tas = game.deste.tas_cek()
            if ceza_tas: alici_oyuncu.tas_al(ceza_tas)
            game._sira_ilerlet(asil_sira_index)
            game.oyun_durumu = GameState.NORMAL_TUR
        alici_oyuncu.el_sirala()
        game.atilan_tas_degerlendirici = None

    @staticmethod
    def atilan_tasi_gecti(game):
        if game.oyun_durumu != GameState.ATILAN_TAS_DEGERLENDIRME: return
        game.atilan_tas_degerlendirici.bir_sonraki()
        if game.atilan_tas_degerlendirici.herkes_gecti_mi():
            yeni_sira_index = game.atilan_tas_degerlendirici.asilin_sirasi()
            game._sira_ilerlet(yeni_sira_index)
            game.oyun_durumu = GameState.NORMAL_TUR
            game.atilan_tas_degerlendirici = None