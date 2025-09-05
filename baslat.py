# baslat.py

from rules.rules_manager import Rules
from core.game_state import GameState
import random
from log import logger

@logger.log_function
def baslat_oyun(game):
    game.mevcut_gorev = random.choice(Rules.GOREVLER)
    game.kazanan_index = None
    game.deste.olustur()
    game.deste.karistir()
    game.sira_kimde_index = 0
    for i, oyuncu in enumerate(game.oyuncular):
        oyuncu.el = []
        tas_sayisi = 14 if i == game.sira_kimde_index else 13
        for _ in range(tas_sayisi):
            oyuncu.tas_al(game.deste.tas_cek())
        oyuncu.el_sirala()
    game.oyun_durumu = GameState.ILK_TUR
    game.atilan_taslar = []
    game.acilan_perler = {i: [] for i in range(len(game.oyuncular))}
    game.turda_tas_cekildi = [False] * len(game.oyuncular)
    game.atilan_tas_degerlendirici = None
    game.acilmis_oyuncular = [False] * len(game.oyuncular)
    game.ilk_el_acan_tur = {}
    # Her oyuncu için hamle yapma durumunu sıfırla
    game.oyuncu_hamle_yapti = [False] * len(game.oyuncular)