# core/player.py
from core.tile import Tile

class Player:
    def __init__(self, isim):
        self.isim = isim
        self.el = []
    def tas_al(self, tas: 'Tile'):
        if tas: self.el.append(tas)
    def tas_at(self, tas_id):
        for i, tas in enumerate(self.el):
            if tas.id == tas_id: return self.el.pop(i)
        return None
    def el_sirala(self):
        def sort_key(t):
            if t.renk == "joker": return (5, 0, 0)
            renk_map = {"kirmizi": 0, "mavi": 1, "siyah": 2, "sari": 3}
            return (renk_map.get(t.renk, 4), 1 if t.deger == 1 else 0, t.deger or 0)
        self.el.sort(key=sort_key)