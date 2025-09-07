# rules/joker_manager.py
from core.tile import Tile
from rules.rules_manager import Rules
from ai.ai_player import AIPlayer
from log import logger

class JokerManager:
    @staticmethod
    @logger.log_function
    def joker_icin_olasi_taslar(taslar):
        jokerler = [t for t in taslar if t.renk == 'joker']
        diger_taslar = [t for t in taslar if t.renk != 'joker']
        if not jokerler: return {}
        if len(jokerler) != 1: return None
        joker = jokerler[0]
        olasi_secimler = {}
        
        # Olası Küt Perler için kontrol
        degerler = {t.deger for t in diger_taslar}
        if len(degerler) == 1 and diger_taslar:
            deger = degerler.pop()
            mevcut_renkler = {t.renk for t in diger_taslar}
            eksik_renkler = list({"sari", "mavi", "siyah", "kirmizi"} - mevcut_renkler)
            if eksik_renkler:
                olasi_secimler[joker] = [Tile(r, deger, f"{r}_{deger}.png", -1) for r in eksik_renkler]
        
        # Olası Seri Perler için kontrol
        renkler = {t.renk for t in diger_taslar}
        if len(renkler) == 1 and diger_taslar:
            renk = renkler.pop()
            sayilar = sorted([t.deger for t in diger_taslar])
            olasi_sayilar = set()
            
            # Serinin içindeki boşlukları bul
            for i in range(len(sayilar) - 1):
                for j in range(sayilar[i] + 1, sayilar[i+1]):
                    olasi_sayilar.add(j)

            # Serinin başına ve sonuna eklenebilecekleri bul
            if sayilar[0] > 1: olasi_sayilar.add(sayilar[0] - 1)
            if sayilar[-1] < 13: olasi_sayilar.add(sayilar[-1] + 1)
            
            # Döngüsel seri (12-13-1) durumunu kontrol et
            if {1, 13}.issubset(sayilar):
                if 12 not in sayilar: olasi_sayilar.add(12)
                if 2 not in sayilar: olasi_sayilar.add(2)
            
            if olasi_sayilar:
                secenekler = [Tile(renk, s, f"{renk}_{s}.png", -1) for s in sorted(list(olasi_sayilar))]
                if joker in olasi_secimler: olasi_secimler[joker].extend(secenekler)
                else: olasi_secimler[joker] = secenekler
        return olasi_secimler if olasi_secimler else None

    @staticmethod
    @logger.log_function
    def el_ac_joker_kontrolu(oyun, oyuncu, secilen_taslar):
        jokerler = [t for t in secilen_taslar if t.renk == 'joker']
        if not jokerler: return {"status": "no_joker"}
        gecerli_mi = Rules.per_dogrula(secilen_taslar, oyun.mevcut_gorev) or Rules.genel_per_dogrula(secilen_taslar)
        olasi_secimler = JokerManager.joker_icin_olasi_taslar(secilen_taslar)
        if not olasi_secimler:
            return {"status": "invalid_joker_move"} if not gecerli_mi else {"status": "no_choice_needed"}
        for joker, secenekler in olasi_secimler.items():
            if isinstance(oyuncu, AIPlayer):
                if secenekler:
                    joker.joker_yerine_gecen = secenekler[0]
                return {"status": "auto_assigned"}
            elif len(secenekler) > 1:
                return {"status": "joker_choice_needed", "options": secenekler, "joker": joker, "secilen_taslar": secilen_taslar}
            elif len(secenekler) == 1:
                joker.joker_yerine_gecen = secenekler[0]
                return {"status": "auto_assigned"}
        return {"status": "no_choice_needed"}