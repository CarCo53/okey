# test_ai_performance.py
import sys
import os
import argparse
import time
import random
from core.tile import Tile
from ai.ai_player import AIPlayer
from rules.rules_manager import Rules
from rules.gorevler import GOREV_LISTESI

# Python'ın mevcut dizinini ve üst dizinlerini sys.path'e ekler
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))


def create_random_hand(num_tiles=25):
    """
    Tüm olası taşları oluşturur ve rastgele bir el seçer.
    Jokerlerin dahil edilme olasılığını artırır.
    """
    renkler = ["sari", "mavi", "siyah", "kirmizi"]
    tum_taslar = []
    
    # 1'den 13'e kadar tüm taşları ikişer adet oluştur
    for renk in renkler:
        for deger in range(1, 14):
            tum_taslar.append(Tile(renk, deger, f"{renk}_{deger}.png"))
            tum_taslar.append(Tile(renk, deger, f"{renk}_{deger}.png"))
    
    # 2 adet joker taşı ekle
    tum_taslar.append(Tile("joker", 0, "okey.png"))
    tum_taslar.append(Tile("joker", 0, "okey.png"))

    # Rastgele bir el seçerken, her zaman en az bir joker eklemeyi dener
    el = random.sample(tum_taslar, num_tiles)
    if not any(t.renk == 'joker' for t in el):
        el[0] = Tile("joker", 0, "okey.png")

    return el

def main():
    parser = argparse.ArgumentParser(description="AI Oyuncunun El Açma Performans Testi")
    parser.add_argument("--gorev", type=str, choices=Rules.GOREVLER, help="AI'nın el açmak için deneyeceği görevi belirler.")
    args = parser.parse_args()

    if not args.gorev:
        print("Lütfen bir görev belirtin. Örneğin: --gorev 'Seri 3'")
        print("Mevcut görevler:", GOREV_LISTESI)
        return

    print(f"--- AI El Açma Testi Başlatılıyor ---")
    print(f"Test Edilecek Görev: {args.gorev}")

    # Yapay zeka oyuncusu oluşturuluyor
    ai_oyuncu = AIPlayer("Test AI", 1)

    # 35 taştan oluşan zorlu bir el oluşturuluyor
    ai_oyuncu.el = create_random_hand()
    ai_oyuncu.el_sirala()
    print(f"Oluşturulan elin taş sayısı: {len(ai_oyuncu.el)}")
    print("Oluşturulan elin taşları:", [f"{t.renk}_{t.deger}" for t in ai_oyuncu.el])

    # Sahte bir Game nesnesi oluşturuluyor
    class MockGame:
        def __init__(self, gorev):
            self.mevcut_gorev = gorev
            self.acilmis_oyuncular = {1: False}
    
    mock_game = MockGame(args.gorev)
    
    # Test başlatılıyor ve süre ölçülüyor
    baslangic_zamani = time.time()
    bulunan_perler = ai_oyuncu.ai_el_ac_dene(mock_game)
    bitis_zamani = time.time()
    
    gecen_sure = bitis_zamani - baslangic_zamani

    # Sonuçlar yazdırılıyor
    print(f"Test Tamamlandı. Geçen Süre: {gecen_sure:.4f} saniye")

    if bulunan_perler:
        print("Geçerli Per(ler) Bulundu!")
        print("Taş ID'leri:", bulunan_perler)
        # Bulunan kombinasyonu daha okunaklı bir şekilde yazdır
        per_taslari = [t for t in ai_oyuncu.el if t.id in bulunan_perler]
        print("Bulunan Perler:")
        if Rules.per_dogrula(per_taslari, args.gorev) is True:
             print([f"{t.renk}_{t.deger}" for t in per_taslari])

    else:
        print("Göreve uygun geçerli bir per bulunamadı.")
    
    print("---------------------------------------")

if __name__ == "__main__":
    main()