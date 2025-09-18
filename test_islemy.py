# Gerekli kütüphaneleri ve sınıfları içe aktar
import sys
import os
import random
from collections import defaultdict
from itertools import combinations

# Kodun bulunduğu dizini Python path'ine ekler
# Bu, core, ai gibi modüllere erişimi sağlar
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from core.tile import Tile
from core.player import Player
from ai.ai_player import AIPlayer
from engine.game_manager import Game
from rules.rules_manager import Rules

# Taş renklerini tanımla
RENKLER = ["sari", "mavi", "siyah", "kirmizi"]

# Yardımcı fonksiyon: Belirtilen renk ve sayılarla seri per oluşturur
def create_seri_per(renk, start, length):
    return [Tile(renk, i, f"{renk}_{i}.png") for i in range(start, start + length)]

# Yardımcı fonksiyon: Belirtilen sayı ve renklerle küt per oluşturur
def create_kut_per(deger, renk_listesi):
    return [Tile(renk, deger, f"{renk}_{deger}.png") for renk in renk_listesi]

# Yardımcı fonksiyon: İçinde joker olan bir per oluşturur
def create_per_with_joker():
    per_tipi = random.choice(["seri", "kut"])
    if per_tipi == "seri":
        renk = random.choice(RENKLER)
        length = random.randint(3, 10)
        start = random.randint(1, 14 - length)
        per = create_seri_per(renk, start, length)
        
        joker_yerine_gecen = random.choice(per)
        joker_tasi = Tile("joker", 0, "okey.png")
        joker_tasi.joker_yerine_gecen = joker_yerine_gecen
        
        per.remove(joker_yerine_gecen)
        per.append(joker_tasi)
    
    else: # per_tipi == "kut"
        deger = random.randint(1, 13)
        renk_sayisi = random.randint(3, 4)
        secilen_renkler = random.sample(RENKLER, renk_sayisi)
        per = create_kut_per(deger, secilen_renkler)
        
        joker_yerine_gecen = random.choice(per)
        joker_tasi = Tile("joker", 0, "okey.png")
        joker_tasi.joker_yerine_gecen = joker_yerine_gecen
        
        per.remove(joker_yerine_gecen)
        per.append(joker_tasi)
        
    return per

# Rastgele perler oluşturan test fonksiyonu
def create_random_perler(count=15):
    perler = []
    for _ in range(count):
        # Bazı perlerde joker olsun, bazıları olmasın
        if random.random() > 0.5:
            perler.append(create_per_with_joker())
        else:
            per_tipi = random.choice(["seri", "kut"])
            if per_tipi == "seri":
                renk = random.choice(RENKLER)
                length = random.randint(3, 10)
                start = random.randint(1, 14 - length)
                perler.append(create_seri_per(renk, start, length))
            elif per_tipi == "kut":
                deger = random.randint(1, 13)
                renk_sayisi = random.randint(3, 4)
                secilen_renkler = random.sample(RENKLER, renk_sayisi)
                perler.append(create_kut_per(deger, secilen_renkler))
    return perler

# Sahte bir Game nesnesi oluşturarak test ortamını hazırlar
class MockGame:
    def __init__(self, acilan_perler, oyuncular):
        self.acilan_perler = acilan_perler
        self.oyuncular = oyuncular
        self.ilk_el_acan_tur = defaultdict(int)
        self.tur_numarasi = 5
        self.acilmis_oyuncular = [False] * len(oyuncular)
        self.oyun_durumu = "NORMAL_TUR"
        self.mevcut_gorev = "Seri 3"

    def joker_degistir(self, degistiren_oyuncu_idx, per_sahibi_idx, per_idx, tas_id):
        # Basit bir simülasyon
        per = self.acilan_perler[per_sahibi_idx][per_idx]
        degistiren_oyuncu = self.oyuncular[degistiren_oyuncu_idx]
        degistirilecek_tas = next((t for t in degistiren_oyuncu.el if t.id == tas_id), None)
        
        if not degistirilecek_tas:
            return False

        for i, per_tasi in enumerate(per):
            if per_tasi.renk == "joker" and per_tasi.joker_yerine_gecen:
                yerine_gecen = per_tasi.joker_yerine_gecen
                if yerine_gecen.renk == degistirilecek_tas.renk and yerine_gecen.deger == degistirilecek_tas.deger:
                    per.pop(i)
                    per.append(degistirilecek_tas)
                    degistiren_oyuncu.el.remove(degistirilecek_tas)
                    degistiren_oyuncu.el.append(per_tasi)
                    per_tasi.joker_yerine_gecen = None
                    return True
        return False

    def islem_yap(self, isleyen_oyuncu_idx, per_sahibi_idx, per_idx, tas_id):
        per = self.acilan_perler[per_sahibi_idx][per_idx]
        isleyen_oyuncu = self.oyuncular[isleyen_oyuncu_idx]
        islenen_tas = next((t for t in isleyen_oyuncu.el if t.id == tas_id), None)
        
        if not islenen_tas:
            return False

        if Rules.islem_dogrula(per, islenen_tas):
            isleyen_oyuncu.el.remove(islenen_tas)
            per.append(islenen_tas)
            return True
        return False
        
# Rastgele el oluşturan yardımcı fonksiyon
def create_random_hand(num_tiles=14):
    tum_taslar = []
    for renk in RENKLER:
        for deger in range(1, 14):
            tum_taslar.append(Tile(renk, deger, f"{renk}_{deger}.png"))
            tum_taslar.append(Tile(renk, deger, f"{renk}_{deger}.png"))
    
    tum_taslar.append(Tile("joker", 0, "okey.png"))
    tum_taslar.append(Tile("joker", 0, "okey.png"))

    return random.sample(tum_taslar, num_tiles)

# Ana test fonksiyonu
def main():
    print("--- AI İşleme Yapma Testi Başlatılıyor ---")
    
    per_listesi = create_random_perler()
    
    acilan_perler_dict = {0: per_listesi}
    
    ai_oyuncu1 = AIPlayer("Test AI 1", 1)
    ai_oyuncu1.el = create_random_hand()
    ai_oyuncu2 = AIPlayer("Test AI 2", 2)
    ai_oyuncu2.el = create_random_hand()
    
    oyuncular = [Player("Oyuncu 0 (Siz)", 0), ai_oyuncu1, ai_oyuncu2]
    
    mock_game = MockGame(acilan_perler_dict, oyuncular)
    
    print(f"Masaya {len(per_listesi)} per açıldı.")
    print("Açılan Perler:")
    for i, per in enumerate(per_listesi):
        print(f"  Per {i+1}: {[f'{t.renk}_{t.deger}{f' (Joker yerine geçen: {t.joker_yerine_gecen.renk}_{t.joker_yerine_gecen.deger})' if t.renk == 'joker' and t.joker_yerine_gecen else ''}' for t in per]}")
    
    print("\n--- AI Oyuncular İşleme Yapıyor ---")
    
    for ai_oyuncu in [ai_oyuncu1, ai_oyuncu2]:
        print(f"\nAI {ai_oyuncu.isim} elini inceliyor...")
        
        mock_game.acilmis_oyuncular[ai_oyuncu.index] = True
        
        islem_yapildi = True
        while islem_yapildi:
            islem_hamlesi = ai_oyuncu.ai_islem_yap_dene(mock_game)
            if islem_hamlesi:
                action_type = islem_hamlesi.get("action_type")
                per_sahibi_idx = islem_hamlesi.get("sahip_idx")
                per_idx = islem_hamlesi.get("per_idx")
                tas_id = islem_hamlesi.get("tas_id")

                if action_type == "joker_degistir":
                    islenen_tas = next((t for t in ai_oyuncu.el if t.id == tas_id), None)
                    print(f"  -> {ai_oyuncu.isim}, 'joker_degistir' hamlesi buldu!")
                    print(f"     Hamle: Elindeki {islenen_tas.renk}_{islenen_tas.deger} taşı ile Per {per_idx+1}'deki jokeri değiştiriyor.")
                    mock_game.joker_degistir(ai_oyuncu.index, per_sahibi_idx, per_idx, tas_id)
                elif action_type == "islem_yap":
                    islenen_tas = next((t for t in ai_oyuncu.el if t.id == tas_id), None)
                    print(f"  -> {ai_oyuncu.isim}, 'islem_yap' hamlesi buldu!")
                    print(f"     Hamle: Elindeki {islenen_tas.renk}_{islenen_tas.deger} taşı, Per {per_idx+1}'e işleniyor.")
                    mock_game.islem_yap(ai_oyuncu.index, per_sahibi_idx, per_idx, tas_id)
                
            else:
                islem_yapildi = False
                print(f"  -> {ai_oyuncu.isim} için başka işleme hamlesi bulunamadı.")
    
    print("\n--- Test Tamamlandı ---")
    
if __name__ == "__main__":
    main()