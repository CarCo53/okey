# test_rules.py

import sys
import os
from itertools import combinations

# rules_manager.py dosyasını içe aktarmak için yol ayarı
# Bu yol, projenizin kök dizinine göre ayarlanmalıdır.
# Örnek:
# sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'carco53', 'okey', 'okey-af103a675f3fd2c486f62d6a82d523ecb771a1e3')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'carco53', 'okey', 'okey-af103a675f3fd2c486f62d6a82d523ecb771a1e3')))

from core.tile import Tile
from rules.rules_manager import Rules

def run_test(test_name, per_taslari, eklenecek_tas, beklenen_sonuc):
    per = [Tile(t[0], t[1], f"{t[0]}_{t[1]}.png") for t in per_taslari]
    tas = Tile(eklenecek_tas[0], eklenecek_tas[1], f"{eklenecek_tas[0]}_{eklenecek_tas[1]}.png")
    
    sonuc = Rules.islem_dogrula(per, tas)
    
    if sonuc != beklenen_sonuc:
        print(f"[HATA] {test_name}: {per_taslari} per'ine {eklenecek_tas} taşını işleme. Beklenen: {beklenen_sonuc}, Alınan: {sonuc}")
        return False
    return True

# Dinamik test senaryoları
renkler = ["sari", "mavi", "siyah", "kirmizi"]

# Normal serilere taş ekleme testleri
print("--- Normal Seri Testleri ---")
for renk in renkler:
    for start_val in range(2, 12):
        for length in range(2, 14 - start_val):
            per_numbers = list(range(start_val, start_val + length))
            per_tiles = [(renk, v) for v in per_numbers]
            
            # Başa ekleme
            eklenecek = (renk, start_val - 1)
            run_test(f"Normal seriye başından ekleme ({renk} {start_val})", per_tiles, eklenecek, True)

            # Sona ekleme
            eklenecek = (renk, start_val + length)
            run_test(f"Normal seriye sonundan ekleme ({renk} {start_val})", per_tiles, eklenecek, True)

# Döngüsel serilere taş ekleme testleri
print("\n--- Döngüsel Seri Testleri ---")
for renk in renkler:
    # 12-13-1 serisi
    per_tiles_12_13_1 = [(renk, 12), (renk, 13), (renk, 1)]
    run_test(f"{renk} 12-13-1 serisine 11 ekleme", per_tiles_12_13_1, (renk, 11), True)
    run_test(f"{renk} 12-13-1 serisine 2 ekleme", per_tiles_12_13_1, (renk, 2), False)
    
    # 1-2-3 serisine 13 ekleme
    per_tiles_1_2_3 = [(renk, 1), (renk, 2), (renk, 3)]
    run_test(f"{renk} 1-2-3 serisine 13 ekleme", per_tiles_1_2_3, (renk, 13), False)

# Küt per testleri
print("\n--- Küt Per Testleri ---")
for deger in range(1, 14):
    colors_to_use = [("sari", deger), ("mavi", deger), ("siyah", deger)]
    per_tiles_3 = [Tile(c, d, f"{c}_{d}.png") for c, d in colors_to_use]
    run_test(f"3 taşlı küt per'e 4. taşı ekleme", per_tiles_3, ("kirmizi", deger), True)

    per_tiles_4 = per_tiles_3 + [Tile("kirmizi", deger, "kirmizi_5.png")]
    run_test(f"4 taşlı küt per'e 5. taşı ekleme", per_tiles_4, ("sari", deger), False)

# Mükerrer taş ekleme testi
print("\n--- Mükerrer Taş Testi ---")
run_test("Aynı taştan bir daha ekleme", [('mavi', 6), ('mavi', 7), ('mavi', 8)], ('mavi', 6), False)
run_test("Mükerrer küt per'e taş ekleme", [('sari', 5), ('mavi', 5), ('kirmizi', 5), ('siyah', 5)], ('mavi', 5), False)
