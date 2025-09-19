# core/deck.py

import random
from core.tile import Tile
from log import logger

class Deck:
    @logger.log_function
    def __init__(self):
        self.taslar = []

    @logger.log_function
    def olustur(self):
        self.taslar = []
        renkler = ["sari", "mavi", "siyah", "kirmizi"]
        for renk in renkler:
            for deger in range(1, 14):
                self.taslar.append(Tile(renk, deger, f"{renk}_{deger}.png"))
                self.taslar.append(Tile(renk, deger, f"{renk}_{deger}.png"))
        self.taslar.append(Tile("joker", 0, "joker.png"))
        self.taslar.append(Tile("joker", 0, "joker.png"))

    @logger.log_function
    def karistir(self):
        random.shuffle(self.taslar)

    @logger.log_function
    def tas_cek(self):
        if self.taslar:
            return self.taslar.pop(0)
        return None

    @logger.log_function
    def tas_ekle(self, tas):
        self.taslar.append(tas)
        random.shuffle(self.taslar)

    def __len__(self):
        return len(self.taslar)