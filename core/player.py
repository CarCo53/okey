# core/player.py
from core.tile import Tile
from log import logger

class Player:
    @logger.log_function
    def __init__(self, isim):
        self.isim = isim
        self.el = []
    @logger.log_function
    def tas_al(self, tas: 'Tile'):
        if tas: self.el.append(tas)
    @logger.log_function
    def tas_at(self, tas_id):
        for i, tas in enumerate(self.el):
            if tas.id == tas_id: return self.el.pop(i)
        return None
    @logger.log_function
    def el_sirala(self):
        @logger.log_function
        def sort_key(t):
            if t.renk == "joker": return (5, 0, 0)
            renk_map = {"kirmizi": 0, "mavi": 1, "siyah": 2, "sari": 3}
            val = t.deger or 0
            is_bir = 1 if val == 1 else 0
            return (renk_map.get(t.renk, 4), is_bir, val)
        self.el.sort(key=sort_key)