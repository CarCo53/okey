# core/deck.py
import random
from core.tile import Tile
from log import logger

class Deck:
    @logger.log_function
    def __init__(self):
        self.taslar = []
        self.olustur()
        self.karistir()
        
    @logger.log_function
    def olustur(self):
        self.taslar = []
        # Her yeni deste oluşturulduğunda ID sayacını sıfırla
        Tile.id_counter = 0
        renkler = ["sari", "mavi", "siyah", "kirmizi"]
        
        # 1'den 13'e kadar olan taşları oluştur
        for renk in renkler:
            for deger in range(1, 14):
                self.taslar.append(Tile(renk, deger, f"{renk}_{deger}.png"))
                self.taslar.append(Tile(renk, deger, f"{renk}_{deger}.png"))
        
        # Okey taşlarını oluştur
        self.taslar.append(Tile("joker", 0, "okey.png"))
        self.taslar.append(Tile("joker", 0, "okey.png"))
        
    @logger.log_function
    def karistir(self):
        random.shuffle(self.taslar)

    @logger.log_function
    def tas_cek(self):
        if self.taslar:
            return self.taslar.pop(0)
        return None