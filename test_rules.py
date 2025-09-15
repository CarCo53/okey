# test_rules.py

import sys
import os
from itertools import combinations, permutations
from collections import Counter
from core.tile import Tile
from rules.rules_manager import Rules
from rules.joker_manager import JokerManager
from rules.per_validators import kut_mu, seri_mu, cift_per_mu, coklu_per_dogrula, karma_per_dogrula

# Bu test dosyası, okey kuralları modülündeki tüm doğrulama
# fonksiyonlarını kapsamlı bir şekilde test etmek için tasarlanmıştır.

def create_tiles(tiles_data):
    """(renk, deger) tuple'larından Tile objeleri oluşturur."""
    return [Tile(renk, deger, f"{renk}_{deger}.png") for renk, deger in tiles_data]

def run_test(test_name, result, expected, is_successful):
    """Test sonucunu kontrol eder ve sadece başarısız olursa çıktı verir."""
    if not is_successful:
        print(f"[HATA] {test_name}: Beklenen: {expected}, Alınan: {result}")
        return False
    return True

def run_all_tests():
    print("--- Tüm Kural Testleri Başlıyor ---")
    
    gecen_testler = 0
    toplam_testler = 0

    # Test 1: Kut Per Doğrulama
    print("\\n--- Küt Per Doğrulama Testleri ---")
    
    renkler = ["sari", "mavi", "siyah", "kirmizi"]
    
    for deger in range(1, 14):
        # 3 taşlı küt per
        toplam_testler += 1
        per_3_tas = create_tiles([("sari", deger), ("mavi", deger), ("siyah", deger)])
        result = kut_mu(per_3_tas)
        gecen_testler += run_test(f"Kut 3 - {deger}", result, True, result)
        
        # 4 taşlı küt per
        toplam_testler += 1
        per_4_tas = per_3_tas + create_tiles([("kirmizi", deger)])
        result = kut_mu(per_4_tas)
        gecen_testler += run_test(f"Kut 4 - {deger}", result, True, result)

        # 5 taşlı küt per (Hatalı Olmalı)
        toplam_testler += 1
        per_5_tas = per_4_tas + create_tiles([("sari", deger)])
        result = kut_mu(per_5_tas)
        gecen_testler += run_test(f"Kut 5 (Hatalı) - {deger}", result, False, not result)
    
    # Jokerli küt perler
    for deger in range(1, 14):
        joker = Tile("joker", 0, "okey.png")
        joker.joker_yerine_gecen = Tile("siyah", deger, "siyah.png")
        
        # 3 taştan 1'i joker
        toplam_testler += 1
        per_joker_1 = create_tiles([("sari", deger), ("mavi", deger)]) + [joker]
        result = kut_mu(per_joker_1)
        gecen_testler += run_test(f"Jokerli Kut 3 - {deger}", result, True, result)
        
        # 4 taştan 1'i joker
        toplam_testler += 1
        per_joker_2 = create_tiles([("sari", deger), ("mavi", deger), ("kirmizi", deger)]) + [joker]
        result = kut_mu(per_joker_2)
        gecen_testler += run_test(f"Jokerli Kut 4 - {deger}", result, True, result)

        # 4 taştan 2'si joker (Hatalı Olmalı)
        joker2 = Tile("joker", 0, "okey.png")
        joker2.joker_yerine_gecen = Tile("kirmizi", deger, "kirmizi.png")
        toplam_testler += 1
        per_joker_3 = create_tiles([("sari", deger), ("mavi", deger)]) + [joker, joker2]
        result = kut_mu(per_joker_3)
        gecen_testler += run_test(f"2 Jokerli Kut 4 (Hatalı) - {deger}", result, False, not result)

    
    # Test 2: Seri Per Doğrulama
    print("\\n--- Seri Per Doğrulama Testleri ---")
    
    for renk in renkler:
        for start_val in range(1, 11):
            for length in range(3, 14 - start_val + 1):
                taslar = create_tiles([(renk, v) for v in range(start_val, start_val + length)])
                toplam_testler += 1
                result = seri_mu(taslar)
                gecen_testler += run_test(f"Seri {length} - {renk} {start_val}-{start_val + length - 1}", result, True, result)
    
    # Döngüsel Seri (12-13-1)
    for renk in renkler:
        toplam_testler += 1
        dongusel_seri = create_tiles([(renk, 12), (renk, 13), (renk, 1)])
        result = seri_mu(dongusel_seri)
        gecen_testler += run_test(f"Döngüsel Seri 12-13-1 - {renk}", result, True, result)
        
        # 1-2-13 serisi (Hatalı)
        toplam_testler += 1
        hatali_dongu = create_tiles([(renk, 1), (renk, 2), (renk, 13)])
        result = seri_mu(hatali_dongu)
        gecen_testler += run_test(f"Hatalı Döngüsel Seri 1-2-13 - {renk}", result, False, not result)

    
    # Test 3: Çift Per Doğrulama
    print("\\n--- Çift Per Doğrulama Testleri ---")
    
    # 4 çift (8 taş)
    toplam_testler += 1
    ciftler = create_tiles([("sari", 1), ("sari", 1), ("mavi", 2), ("mavi", 2), ("siyah", 3), ("siyah", 3), ("kirmizi", 4), ("kirmizi", 4)])
    result = cift_per_mu(ciftler)
    gecen_testler += run_test("4 Çift (8 taş)", result, True, result)
    
    # 4 çiftten az (6 taş)
    toplam_testler += 1
    az_cift = ciftler[:6]
    result = cift_per_mu(az_cift)
    gecen_testler += run_test("Az Çift (6 taş)", result, False, not result)
    
    # Jokerli çiftler
    toplam_testler += 1
    jokerli_ciftler = create_tiles([("sari", 1), ("sari", 1), ("mavi", 2)])
    joker_1 = Tile("joker", 0, "okey.png")
    jokerli_ciftler.append(joker_1)
    result = cift_per_mu(jokerli_ciftler)
    gecen_testler += run_test("Jokerli Çift (3 taş)", result, False, not result)

    toplam_testler += 1
    joker_2 = Tile("joker", 0, "okey.png")
    jokerli_ciftler.append(joker_2)
    result = cift_per_mu(jokerli_ciftler)
    gecen_testler += run_test("2 Jokerli Çift (4 taş)", result, False, not result)
    
    # 3 çift + 2 joker
    toplam_testler += 1
    uc_cift_iki_joker = create_tiles([("sari", 1),("sari", 1),("mavi", 2),("mavi", 2),("siyah", 3),("siyah", 3)]) + [joker_1, joker_2]
    result = cift_per_mu(uc_cift_iki_joker)
    gecen_testler += run_test("3 Çift + 2 Joker (8 taş)", result, True, result)
    
    # Test 4: Çoklu ve Karma Per Doğrulama
    print("\\n--- Çoklu ve Karma Per Doğrulama Testleri ---")
    
    # 2x Küt 3
    toplam_testler += 1
    coklu_kut = create_tiles([("sari", 5),("mavi", 5),("siyah", 5),("sari", 8),("mavi", 8),("kirmizi", 8)])
    result = coklu_per_dogrula(coklu_kut, "küt", 3, 2)
    gecen_testler += run_test("2x Küt 3", result, True, result)
    
    # Küt 3 + Seri 3
    toplam_testler += 1
    karma = create_tiles([("sari", 5),("mavi", 5),("siyah", 5),("kirmizi", 10),("kirmizi", 11),("kirmizi", 12)])
    result = karma_per_dogrula(karma, 3)
    gecen_testler += run_test("Küt 3 + Seri 3", result, True, result)

    # Test 5: İşlem Doğrulama (Per'e Taş Ekleme)
    print("\\n--- İşlem Doğrulama Testleri ---")
    
    # Kut per'e normal taş ekleme
    toplam_testler += 1
    per_kut = create_tiles([("sari", 5),("mavi", 5),("siyah", 5)])
    tas_eklenecek = Tile("kirmizi", 5, "kirmizi_5.png")
    result = Rules.islem_dogrula(per_kut, tas_eklenecek)
    gecen_testler += run_test("Küt 3'e 4. taşı ekleme", result, True, result)
    
    # Seri per'e normal taş ekleme (baştan)
    toplam_testler += 1
    per_seri = create_tiles([("mavi", 6),("mavi", 7),("mavi", 8)])
    tas_eklenecek = Tile("mavi", 5, "mavi_5.png")
    result = Rules.islem_dogrula(per_seri, tas_eklenecek)
    gecen_testler += run_test("Seri'ye baştan taş ekleme", result, True, result)
    
    # Seri per'e normal taş ekleme (sondan)
    toplam_testler += 1
    per_seri = create_tiles([("mavi", 6),("mavi", 7),("mavi", 8)])
    tas_eklenecek = Tile("mavi", 9, "mavi_9.png")
    result = Rules.islem_dogrula(per_seri, tas_eklenecek)
    gecen_testler += run_test("Seri'ye sondan taş ekleme", result, True, result)
    
    # Seri per'e joker ekleme
    toplam_testler += 1
    per_seri = create_tiles([("mavi", 6),("mavi", 8)])
    joker_eklenecek = Tile("joker", 0, "okey.png")
    joker_eklenecek.joker_yerine_gecen = None
    result = Rules.islem_dogrula(per_seri, joker_eklenecek)
    gecen_testler += run_test("Seri'ye joker ekleme", result, True, result)

    # Hatalı işlem (farklı renk)
    toplam_testler += 1
    per_seri = create_tiles([("mavi", 6),("mavi", 7),("mavi", 8)])
    tas_hatali = Tile("sari", 9, "sari_9.png")
    result = Rules.islem_dogrula(per_seri, tas_hatali)
    gecen_testler += run_test("Seri'ye hatalı renk taş ekleme", result, False, not result)
    
    # Hatalı işlem (joker olmayan per'e joker ekleme)
    # Bu durum JokerManager içinde ele alınıyor, burada zaten _seri_islem_dogrula
    # fonksiyonu üzerinden test ediliyor.

    # Test 6: Joker Değiştirme
    print("\\n--- Joker Değiştirme ve Olasılık Testleri ---")
    
    # Seri per'de joker değiştirme
    per_seri = create_tiles([("mavi", 6),("mavi", 8)])
    joker_tas = Tile("joker", 0, "okey.png")
    joker_tas.joker_yerine_gecen = Tile("mavi", 7, "mavi_7.png")
    per_seri.append(joker_tas)
    
    oyuncu_elindeki_tas = Tile("mavi", 7, "mavi_7.png")
    
    toplam_testler += 1
    result = JokerManager.el_ac_joker_kontrolu(None, None, per_seri)
    gecen_testler += run_test("Joker icin olasi taslar", "joker_choice_needed", result["status"], result["status"] == "joker_choice_needed")

    if result["status"] == "joker_choice_needed":
        toplam_testler += 1
        expected_options = set([t.deger for t in result["options"]])
        test_options = set([6, 8])
        gecen_testler += run_test("Joker secim seçenekleri", expected_options, test_options, expected_options == test_options)
        
    print(f"\\nToplam Test: {toplam_testler}, Başarılı: {gecen_testler}")

if __name__ == "__main__":
    run_all_tests()