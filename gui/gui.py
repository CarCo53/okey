# gui/gui.py
import tkinter as tk
from gui.visuals import Visuals
from gui.buttons import ButtonManager
from gui.status import StatusBar
from core.game_state import GameState
from gui.arayuzguncelle import arayuzu_guncelle
from engine.game_manager import Game 

class Arayuz:
    def __init__(self, oyun: Game):
        self.oyun = oyun
        self.oyun.arayuz = self
        self.pencere = tk.Tk()
        self.pencere.title("Okey Oyunu")
        self.pencere.geometry("1400x900")
        self.visuals = Visuals()
        self.visuals.yukle()
        self.statusbar = StatusBar(self)
        self.button_manager = ButtonManager(self)
        self.secili_tas_idler = []
        self.alanlar = {}
        self._layout_olustur()
        self.arayuzu_guncelle()

    def _layout_olustur(self):
        # ... (Bu fonksiyonun içeriği aynı kalabilir) ...
        pass

    def arayuzu_guncelle(self):
        arayuzu_guncelle(self)

    def tas_sec(self, tas_id):
        if tas_id in self.secili_tas_idler: self.secili_tas_idler.remove(tas_id)
        else: self.secili_tas_idler.append(tas_id)
        self.arayuzu_guncelle()

    def per_sec(self, oyuncu_index, per_index):
        if len(self.secili_tas_idler) != 1:
            self.statusbar.guncelle("İşlemek için elinizden 1 taş seçmelisiniz.")
            return
        sonuc = self.oyun.islem_yap(0, oyuncu_index, per_index, self.secili_tas_idler[0])
        if sonuc:
            self.secili_tas_idler = []
            self.statusbar.guncelle("Hamle başarılı!")
        else:
            self.statusbar.guncelle("Geçersiz hamle! (El açtığınız turda işleme yapamazsınız)")
        self.arayuzu_guncelle()
            
    def joker_secim_penceresi_ac(self, secenekler, joker, secilen_taslar):
        # ... (Bu fonksiyonun içeriği aynı kalabilir) ...
        pass

    def joker_secildi(self, secilen_deger, joker, secilen_taslar, pencere):
        pencere.destroy()
        sonuc = self.oyun.el_ac_joker_ile(0, secilen_taslar, joker, secilen_deger)
        if sonuc and sonuc.get("status") == "success":
            self.secili_tas_idler = []
        self.arayuzu_guncelle()
    
    def ai_oynat(self):
        oyun = self.oyun
        if oyun.oyun_bitti_mi():
            self.arayuzu_guncelle()
            return

        sira_index = oyun.sira_kimde_index
        if sira_index != 0 and isinstance(oyun.oyuncular[sira_index], AIPlayer):
            ai_oyuncu = oyun.oyuncular[sira_index]
            
            if oyun.oyun_durumu == GameState.ATILAN_TAS_DEGERLENDIRME:
                degerlendiren_idx = oyun.atilan_tas_degerlendirici.siradaki()
                if degerlendiren_idx == sira_index:
                    atilan_tas = oyun.atilan_taslar[-1]
                    if ai_oyuncu.atilan_tasi_degerlendir(oyun, atilan_tas):
                        oyun.atilan_tasi_al(sira_index)
                    else:
                        oyun.atilan_tasi_gecti()
                    self.arayuzu_guncelle()
            
            elif oyun.oyun_durumu in [GameState.NORMAL_TUR, GameState.NORMAL_TAS_ATMA]:
                # AI Beyni burada çalışır
                if oyun.oyun_durumu == GameState.NORMAL_TUR:
                    oyun.desteden_cek(sira_index)
                    self.arayuzu_guncelle()

                elini_acti_mi = oyun.acilmis_oyuncular[sira_index]
                el_acan_tur = oyun.ilk_el_acan_tur.get(sira_index)

                if not elini_acti_mi:
                    ac_kombo = ai_oyuncu.ai_el_ac_dene(oyun)
                    if ac_kombo:
                        oyun.el_ac(sira_index, ac_kombo)
                        self.arayuzu_guncelle()
                
                # Sadece elini önceki turlarda açtıysa işleme yapabilir
                elif el_acan_tur is not None and oyun.tur_numarasi > el_acan_tur:
                    islem_hamlesi = ai_oyuncu.ai_islem_yap_dene(oyun)
                    if islem_hamlesi:
                        oyun.islem_yap(sira_index, **islem_hamlesi)
                        self.arayuzu_guncelle()

                # Her durumda en son taş atar
                tas_to_discard = ai_oyuncu.karar_ver_ve_at(oyun)
                if tas_to_discard:
                    oyun.tas_at(sira_index, tas_to_discard.id)
                self.arayuzu_guncelle()
        
        self.pencere.after(500, self.ai_oynat)

    def baslat(self):
        self.pencere.mainloop()