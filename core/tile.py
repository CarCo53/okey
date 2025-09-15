# core/tile.py
import uuid
from log import logger

class Tile:
    RENK_SIRALAMASI = {"sari": 0, "mavi": 1, "siyah": 2, "kirmizi": 3, "joker": 4}
    id_counter = 0

    @logger.log_function
    def __init__(self, renk, deger, imaj_adi):
        # Taşlara artan bir sayısal ID atar.
        Tile.id_counter += 1
        self.id = Tile.id_counter
        self.renk = renk
        self.deger = deger
        self.imaj_adi = imaj_adi
        self.joker_yerine_gecen = None
        self.renk_sira = self.RENK_SIRALAMASI.get(self.renk)

    def __repr__(self):
        if self.renk == "joker":
            return f"Joker({self.id})"
        return f"{self.renk}_{self.deger}_{self.id}"

    def __eq__(self, other):
        if not isinstance(other, Tile):
            return NotImplemented
        return self.id == other.id

    def __hash__(self):
        return hash(self.id)