from log import logger
# core/game_state.py
class GameState:
    ILK_TUR = "ILK_TUR"
    NORMAL_TUR = "NORMAL_TUR"
    ATILAN_TAS_DEGERLENDIRME = "ATILAN_TAS_DEGERLENDIRME"
    NORMAL_TAS_ATMA = "NORMAL_TAS_ATMA"
    BITIS = "BITIS"

class AtilanTasDegerlendirici:
    @logger.log_function
    def __init__(self, tasi_atan_index, oyuncu_sayisi=4):
        self.tasi_atan_index = tasi_atan_index
        self.oyuncu_sayisi = oyuncu_sayisi
        self.degerlendiren_index = (tasi_atan_index + 1) % oyuncu_sayisi
    def siradaki(self):
        return self.degerlendiren_index
    @logger.log_function
    def bir_sonraki(self):
        self.degerlendiren_index = (self.degerlendiren_index + 1) % self.oyuncu_sayisi
    @logger.log_function
    def asilin_sirasi(self):
        return (self.tasi_atan_index + 1) % self.oyuncu_sayisi
    @logger.log_function
    def herkes_gecti_mi(self):
        return self.degerlendiren_index == self.tasi_atan_index