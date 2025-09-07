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
        # Sadece bir joker için seçim yapılır, birden fazla joker varsa bu durumu atla
        if len(jokerler) != 1:
            return None

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
            
            # Döngüsel seri (12-13-1 gibi) durumunu kontrol et
            if 1 in sayilar and 13 in sayilar:
                if len(sayilar) > 2 and 12 not in sayilar:
                    olasi_sayilar.add(12)
                if sayilar[0] == 1 and sayilar[-1] == 13:
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
        
        # Sadece per doğrulaması yapıyoruz, jokerin atanması için değil.
        # AI oyuncular için özel bir durum olabilir ancak insan oyuncu için her zaman sorulmalı.
        gecerli_mi = Rules.per_dogrula(secilen_taslar, oyun.mevcut_gorev) or Rules.genel_per_dogrula(secilen_taslar)
        
        olasi_secimler = JokerManager.joker_icin_olasi_taslar(secilen_taslar)
        
        # Eğer per geçerli ve tek bir joker varsa, seçenekleri kontrol et.
        if gecerli_mi and len(jokerler) == 1:
            if olasi_secimler and len(olasi_secimler.get(jokerler[0], [])) > 1:
                return {"status": "joker_choice_needed", "options": olasi_secimler[jokerler[0]], "joker": jokerler[0], "secilen_taslar": secilen_taslar}
            elif olasi_secimler and len(olasi_secimler.get(jokerler[0], [])) == 1:
                jokerler[0].joker_yerine_gecen = olasi_secimler[jokerler[0]][0]
                return {"status": "auto_assigned"}
            elif not olasi_secimler:
                # Sadece jokerle açılan durumlarda (örn: 3 jokerden küt 3), jokerin ne olduğunu sormasına gerek yok.
                # Ancak bu durumları daha net belirlemek gerek. Şimdilik bu varsayımla devam edelim.
                return {"status": "no_choice_needed"}

        if isinstance(oyuncu, AIPlayer) and olasi_secimler and olasi_secimler.get(jokerler[0]):
             jokerler[0].joker_yerine_gecen = olasi_secimler[jokerler[0]][0]
             return {"status": "auto_assigned"}

        # Hiç joker yoksa veya joker geçerli bir per oluşturmuyorsa
        if not gecerli_mi:
            return {"status": "invalid_joker_move", "message": "Joker ile geçersiz per açamazsınız."}
            
        return {"status": "no_choice_needed"}