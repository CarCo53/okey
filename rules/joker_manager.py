# rules/joker_manager.py

from core.tile import Tile
from rules.per_validators import seri_mu, kut_mu
from log import logger

class JokerManager:
    @staticmethod
    @logger.log_function
    def el_ac_joker_kontrolu(game, oyuncu, secilen_taslar):
        joker = next((t for t in secilen_taslar if t.renk == "joker"), None)
        if not joker:
            return {"status": "no_joker"}
        
        diger_taslar = [t for t in secilen_taslar if t.id != joker.id]
        
        if not diger_taslar or len(diger_taslar) < 2:
            return {"status": "invalid_joker_move", "message": "Jokerle per açmak için en az iki taş daha seçmelisiniz."}
        
        is_seri_potansiyeli = len({t.renk for t in diger_taslar}) == 1
        is_kut_potansiyeli = len({t.deger for t in diger_taslar}) == 1
        
        if is_seri_potansiyeli:
            return {"status": "joker_choice_needed", "options": JokerManager.joker_icin_olasi_taslar(diger_taslar), "joker": joker, "secilen_taslar": secilen_taslar}
        if is_kut_potansiyeli and len(diger_taslar) <= 3:
            return {"status": "joker_choice_needed", "options": JokerManager.joker_icin_olasi_taslar(diger_taslar), "joker": joker, "secilen_taslar": secilen_taslar}
        
        return {"status": "invalid_joker_move"}
    
    @staticmethod
    @logger.log_function
    def joker_icin_olasi_taslar(diger_taslar):
        olasi_taslar = []
        
        # Seri için
        if len({t.renk for t in diger_taslar}) == 1:
            renk = diger_taslar[0].renk
            sayilar = sorted([t.deger for t in diger_taslar])
            
            if len(sayilar) == 2 and sayilar[1] - sayilar[0] == 2:
                olasi_taslar.append(Tile(renk, sayilar[0] + 1, f"{renk}_{sayilar[0]+1}.png"))
            else:
                if sayilar[0] > 1:
                    olasi_taslar.append(Tile(renk, sayilar[0] - 1, f"{renk}_{sayilar[0]-1}.png"))
                if sayilar[-1] < 13:
                    olasi_taslar.append(Tile(renk, sayilar[-1] + 1, f"{renk}_{sayilar[-1]+1}.png"))
            
            # 1-13 döngüsü için
            if 1 in sayilar and 13 in sayilar:
                if len(sayilar) == 2:
                    olasi_taslar.append(Tile(renk, 12, f"{renk}_{12}.png"))
        
        # Küt için
        elif len({t.deger for t in diger_taslar}) == 1 and len(diger_taslar) <= 3:
            deger = diger_taslar[0].deger
            renkler_mevcut = {t.renk for t in diger_taslar}
            tum_renkler = ["sari", "mavi", "siyah", "kirmizi"]
            for renk in tum_renkler:
                if renk not in renkler_mevcut:
                    olasi_taslar.append(Tile(renk, deger, f"{renk}_{deger}.png"))
        
        return olasi_taslar