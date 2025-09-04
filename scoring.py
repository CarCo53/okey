from log import logger
# scoring.py
@logger.log_function
def puan_hesapla(oyuncular):
    puanlar = []
    for oyuncu in oyuncular:
        toplam = sum(tas.deger if tas.deger else 0 for tas in oyuncu.el)
        puanlar.append(toplam)
    return puanlar