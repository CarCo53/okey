# core/player.py
from log import logger
from core.tile import Tile

class Player:
    @logger.log_function
    def __init__(self, isim, index):
        self.isim = isim
        self.el = []
        self.index = index
        self.acilmis_perler = []
    
    @logger.log_function
    def tas_al(self, tas: Tile):
        self.el.append(tas)
        self.el_sirala()

    @logger.log_function
    def tas_at(self, tas_id):
        atilan_tas = next((t for t in self.el if t.id == tas_id), None)
        if atilan_tas:
            self.el.remove(atilan_tas)
            self.el_sirala()
            return atilan_tas
        return None

    @logger.log_function
    def el_sirala(self):
        self.el.sort(key=lambda t: (t.renk_sira, t.deger))