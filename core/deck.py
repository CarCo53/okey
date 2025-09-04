# core/deck.py
import random
from core.tile import Tile
from utils import benzersiz_id_uret

class Deck:
    def __init__(self):
        self.taslar = []
    def olustur(self):
        self.taslar = []
        renkler = ["sari", "mavi", "siyah", "kirmizi"]
        for renk in renkler:
            for deger in range(1, 14):
                for _ in range(2):
                    self.taslar.append(Tile(renk, deger, f"{renk}_{deger}.png", benzersiz_id_uret()))
        for _ in range(2):
            self.taslar.append(Tile("joker", None, "fake_okey.png", benzersiz_id_uret()))
    def karistir(self):
        random.shuffle(self.taslar)
    def tas_cek(self):
        return self.taslar.pop() if self.taslar else None