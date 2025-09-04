# engine/action_manager.py
from rules.rules_manager import Rules
from rules.joker_manager import JokerManager
from core.game_state import GameState
from log import logger

class ActionManager:
    @staticmethod
    @logger.log_function
    def el_ac(game, oyuncu_index, tas_id_list):
        oyuncu = game.oyuncular[oyuncu_index]
        secilen_taslar = [tas for tas in oyuncu.el if tas.id in tas_id_list]
        joker_kontrol_sonucu = JokerManager.el_ac_joker_kontrolu(game, oyuncu, secilen_taslar)
        if joker_kontrol_sonucu["status"] == "joker_choice_needed":
            return joker_kontrol_sonucu
        if joker_kontrol_sonucu["status"] == "invalid_joker_move":
            return {"status": "fail", "message": "Jokerle geçersiz per açamazsınız."}
        return ActionManager._eli_ac_ve_isle(game, oyuncu_index, secilen_taslar)

    @staticmethod
    @logger.log_function
    def _eli_ac_ve_isle(game, oyuncu_index, secilen_taslar):
        oyuncu = game.oyuncular[oyuncu_index]
        is_ilk_acilis = not game.acilmis_oyuncular[oyuncu_index]
        dogrulama_sonucu = False
        if is_ilk_acilis:
            dogrulama_sonucu = Rules.per_dogrula(secilen_taslar, game.mevcut_gorev)
        else:
            dogrulama_sonucu = Rules.genel_per_dogrula(secilen_taslar)
        if dogrulama_sonucu:
            if is_ilk_acilis:
                game.acilmis_oyuncular[oyuncu_index] = True
                game.ilk_el_acan_tur[oyuncu_index] = game.tur_numarasi
            for tas in secilen_taslar:
                oyuncu.tas_at(tas.id)
            if isinstance(dogrulama_sonucu, tuple):
                for per in dogrulama_sonucu: game._per_sirala(per)
                game.acilan_perler[oyuncu_index].extend(dogrulama_sonucu)
            else: 
                game._per_sirala(secilen_taslar)
                game.acilan_perler[oyuncu_index].append(secilen_taslar)
            oyuncu.el_sirala()
            game.oyun_durumu = GameState.NORMAL_TAS_ATMA
            return {"status": "success"}
        else:
            for tas in secilen_taslar:
                if tas.renk == 'joker': tas.joker_yerine_gecen = None
            return {"status": "fail", "message": "Geçersiz per."}

    @staticmethod
    @logger.log_function
    def islem_yap(game, isleyen_oyuncu_idx, per_sahibi_idx, per_idx, tas_id):
        el_acan_tur = game.ilk_el_acan_tur.get(isleyen_oyuncu_idx)
        if el_acan_tur is not None and game.tur_numarasi <= el_acan_tur:
            logger.warning(f"Oyuncu {isleyen_oyuncu_idx} elini açtığı turda işleme yapamaz.")
            return False
        if not game.acilmis_oyuncular[isleyen_oyuncu_idx] or isleyen_oyuncu_idx != game.sira_kimde_index:
            return False
        oyuncu = game.oyuncular[isleyen_oyuncu_idx]
        tas = next((t for t in oyuncu.el if t.id == tas_id), None)
        if not tas: return False
        per = game.acilan_perler[per_sahibi_idx][per_idx]
        for i, per_tasi in enumerate(per):
            if per_tasi.renk == "joker" and per_tasi.joker_yerine_gecen:
                yerine_gecen = per_tasi.joker_yerine_gecen
                if yerine_gecen.renk == tas.renk and yerine_gecen.deger == tas.deger:
                    joker = per.pop(i)
                    joker.joker_yerine_gecen = None
                    oyuncu.tas_al(joker)
                    oyuncu.tas_at(tas.id)
                    per.append(tas)
                    oyuncu.el_sirala()
                    game._per_sirala(per)
                    game.oyun_durumu = GameState.NORMAL_TAS_ATMA
                    return True
        if Rules.islem_dogrula(per, tas):
            oyuncu.tas_at(tas.id)
            per.append(tas)
            game._per_sirala(per)
            game.oyun_durumu = GameState.NORMAL_TAS_ATMA
            if not oyuncu.el:
                game.oyun_durumu = GameState.BITIS
                game.kazanan_index = isleyen_oyuncu_idx
            return True
        return False