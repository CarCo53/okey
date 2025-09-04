# core/tile.py
class Tile:
    def __init__(self, renk, deger, imaj_adi, id):
        self.renk = renk
        self.deger = deger
        self.imaj_adi = imaj_adi
        self.id = id
        self.joker_yerine_gecen = None 

    def __repr__(self):
        if self.joker_yerine_gecen:
            return f"Okey(yerine={self.joker_yerine_gecen.renk}_{self.joker_yerine_gecen.deger})"
        if self.renk == "joker":
            return f"Joker({self.id})"
        return f"{self.renk}_{self.deger}_{self.id}"