# gui/gui.py
import tkinter as tk
from gui.visuals import Visuals
from gui.buttons import ButtonManager
from gui.status import StatusBar
from core.game_state import GameState
from gui.arayuzguncelle import arayuzu_guncelle
from engine.game_manager import Game 
from ai.ai_player import AIPlayer
from log import logger

class Arayuz:
    @logger.log_function
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

    @logger.log_function
    def _layout_olustur(self):
        self.statusbar.ekle_status_label(self.pencere)
        oyuncu_cercevesi = tk.Frame(self.pencere)
        oyuncu_cercevesi.pack(pady=5, fill="x")
        self.alanlar['oyuncu_1'] = self._oyuncu_alani_olustur(oyuncu_cercevesi, "Oyuncu 1 (Siz)")
        self.alanlar['oyuncu_2'] = self._oyuncu_alani_olustur(oyuncu_cercevesi, "AI Oyuncu 2")
        self.alanlar['oyuncu_3'] = self._oyuncu_alani_olustur(oyuncu_cercevesi, "AI Oyuncu 3")
        self.alanlar['oyuncu_4'] = self._oyuncu_alani_olustur(oyuncu_cercevesi, "AI Oyuncu 4")
        self.masa_frame = tk.LabelFrame(self.pencere, text="Masa (Açılan Perler)", padx=10, pady=10)
        self.masa_frame.pack(pady=10, fill="both", expand=True)
        deste_ve_atilan_cerceve = tk.Frame(self.pencere)
        deste_ve_atilan_cerceve.pack(pady=5)
        self.deste_frame = tk.LabelFrame(deste_ve_atilan_cerceve, text="Deste", padx=5, pady=5)
        self.deste_frame.pack(side=tk.LEFT, padx=10)
        self.atilan_frame = tk.LabelFrame(deste_ve_atilan_cerceve, text="Atılan Taşlar", padx=5, pady=5)
        self.atilan_frame.pack(side=tk.LEFT, padx=10)
        self.deste_sayisi_label = tk.Label(self.deste_frame, text="", font=("Arial", 12, "bold"))
        self.deste_sayisi_label.pack(side=tk.TOP, pady=2)
        self.button_manager.ekle_butonlar(self.pencere)

    @logger.log_function
    def _oyuncu_alani_olustur(self, parent, isim):
        frame = tk.LabelFrame(parent, text=isim, padx=5, pady=5)
        frame.pack(pady=2, fill="x")
        return frame

    @logger.log_function
    def arayuzu_guncelle(self):
        arayuzu_guncelle(self)

    @logger.log_function
    def tas_sec(self, tas_id):
        if tas_id in self.secili_tas_idler: self.secili_tas_idler.remove(tas_id)
        else: self.secili_tas_idler.append(tas_id)
        self.arayuzu_guncelle()

    @logger.log_function
    def per_sec(self, oyuncu_index, per_index):
        if len(self.secili_tas_idler) != 1:
            self.statusbar.guncelle("İşlemek için elinizden 1 taş seçmelisiniz.")
            return
        sonuc = self.oyun.islem_yap(0, oyuncu_index, per_index, self.secili_tas_idler[0])
        if sonuc:
            self.secili_tas_idler = []
        else:
            self.statusbar.guncelle("Geçersiz hamle! (El açtığınız turda işleme yapamazsınız)")
        self.arayuzu_guncelle()
            
    @logger.log_function
    def joker_secim_penceresi_ac(self, secenekler, joker, secilen_taslar):
        secim_penceresi = tk.Toplevel(self.pencere)
        secim_penceresi.title("Joker Seçimi")
        secim_penceresi.geometry("300x150")
        secim_penceresi.transient(self.pencere)
        secim_penceresi.grab_set()
        tk.Label(secim_penceresi, text="Joker'i hangi taş yerine kullanmak istersiniz?").pack(pady=10)
        buttons_frame = tk.Frame(secim_penceresi)
        buttons_frame.pack(pady=10)
        for tas_secenek in secenekler:
            img = self.visuals.tas_resimleri.get(tas_secenek.imaj_adi)
            if img:
                b = tk.Button(buttons_frame, image=img,
                              command=lambda s=tas_secenek: self.joker_secildi(s, joker, secilen_taslar, secim_penceresi))
                b.pack(side=tk.LEFT, padx=5)

    @logger.log_function
    def joker_secildi(self, secilen_deger, joker, secilen_taslar, pencere):
        pencere.destroy()
        self.oyun.el_ac_joker_ile(0, secilen_taslar, joker, secilen_deger)
        self.secili_tas_idler = []
        self.arayuzu_guncelle()
    
    def ai_oynat(self):
        oyun = self.oyun
        if oyun.oyun_bitti_mi():
            self.arayuzu_guncelle()
            return

        sira_index = oyun.sira_kimde_index
        
        # Sadece AI sırası ise ve oyun bitmediyse devam et
        if sira_index != 0 and isinstance(oyun.oyuncular[sira_index], AIPlayer):
            ai_oyuncu = oyun.oyuncular[sira_index]
            
            # --- ATILAN TAŞI DEĞERLENDİRME AŞAMASI ---
            if oyun.oyun_durumu == GameState.ATILAN_TAS_DEGERLENDIRME:
                degerlendiren_idx = oyun.atilan_tas_degerlendirici.siradaki()
                if degerlendiren_idx == sira_index:
                    logger.info(f"AI {sira_index} atılan taşı değerlendiriyor.")
                    atilan_tas = oyun.atilan_taslar[-1]
                    if ai_oyuncu.atilan_tasi_degerlendir(oyun, atilan_tas):
                        oyun.atilan_tasi_al(sira_index)
                    else:
                        oyun.atilan_tasi_gecti()
                    self.arayuzu_guncelle()
            
            # --- NORMAL TUR AKIŞI ---
            elif oyun.oyun_durumu in [GameState.NORMAL_TUR, GameState.NORMAL_TAS_ATMA]:
                logger.info(f"Sıra AI {sira_index}'de. Durum: {oyun.oyun_durumu}")

                # 1. TAŞ ÇEKME (Gerekliyse)
                if oyun.oyun_durumu == GameState.NORMAL_TUR:
                    oyun.desteden_cek(sira_index)
                    self.arayuzu_guncelle()

                # 2. HAMLE YAPMA
                elini_acti_mi = oyun.acilmis_oyuncular[sira_index]
                
                # A. Henüz elini açmadıysa, açmayı dener
                if not elini_acti_mi:
                    ac_kombo = ai_oyuncu.ai_el_ac_dene(oyun)
                    if ac_kombo:
                        oyun.el_ac(sira_index, ac_kombo)
                        self.arayuzu_guncelle()
                        # Elini açtığı için bu tur başka hamle yapamaz, doğrudan taş atar
                
                # B. Eli zaten açıksa ve işlem yapma sırası geldiyse
                elif oyun.ilk_el_acan_tur.get(sira_index, -1) < oyun.tur_numarasi:
                    islem_yapildi = True
                    while islem_yapildi: # İşlenecek taş kalmayana kadar döner
                        islem_hamlesi = ai_oyuncu.ai_islem_yap_dene(oyun)
                        if islem_hamlesi:
                            oyun.islem_yap(sira_index, **islem_hamlesi)
                            self.arayuzu_guncelle()
                        else:
                            islem_yapildi = False

                # 3. TAŞ ATMA
                if ai_oyuncu.el:
                    tas_to_discard = ai_oyuncu.karar_ver_ve_at(oyun)
                    if tas_to_discard:
                        oyun.tas_at(sira_index, tas_to_discard.id)
                    else: # Atacak taş bulamazsa (eli bittiyse)
                        oyun.oyun_durumu = GameState.BITIS
                        oyun.kazanan_index = sira_index
                self.arayuzu_guncelle()
        
        self.pencere.after(750, self.ai_oynat) # Gecikmeyi biraz artırdım

    @logger.log_function
    def baslat(self):
        self.pencere.mainloop()