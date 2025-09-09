# gui/buttons.py
import tkinter as tk
from core.game_state import GameState
from log import logger

class ButtonManager:
    @logger.log_function
    def __init__(self, arayuz):
        self.arayuz = arayuz
        self.butonlar = {}

    def ekle_butonlar(self, parent):
        frame = tk.Frame(parent)
        frame.pack(pady=10)
        self.butonlar["yerden_al"] = tk.Button(frame, text="Yerden Al", command=self.yerden_al)
        self.butonlar["gec"] = tk.Button(frame, text="Geç", command=self.gec)
        self.butonlar["desteden_cek"] = tk.Button(frame, text="Desteden Çek", command=self.desteden_cek)
        self.butonlar["el_ac"] = tk.Button(frame, text="Elini Aç", command=self.el_ac)
        self.butonlar["tas_at"] = tk.Button(frame, text="Taş At", command=self.tas_at)
        self.butonlar["yeni_oyun"] = tk.Button(frame, text="Yeni Oyun", command=self.yeni_oyun)
        
        for btn in self.butonlar.values():
            btn.pack(side=tk.LEFT, padx=8)

    
    def butonlari_guncelle(self, oyun_durumu):
        for btn in self.butonlar.values():
            btn.config(state=tk.DISABLED)
        
        oyun = self.arayuz.oyun
        sira_bende = oyun.sira_kimde_index == 0
        
        if oyun_durumu == GameState.ILK_TUR and sira_bende:
            self.butonlar["tas_at"].config(state=tk.NORMAL)
        elif oyun_durumu == GameState.NORMAL_TUR and sira_bende:
            self.butonlar["el_ac"].config(state=tk.NORMAL)
            self.butonlar["desteden_cek"].config(state=tk.NORMAL)
        elif oyun_durumu == GameState.ATILAN_TAS_DEGERLENDIRME:
            degerlendiren_ben_miyim = oyun.atilan_tas_degerlendirici and oyun.atilan_tas_degerlendirici.siradaki() == 0
            if degerlendiren_ben_miyim:
                self.butonlar["yerden_al"].config(state=tk.NORMAL)
                self.butonlar["gec"].config(state=tk.NORMAL)
        elif oyun_durumu == GameState.NORMAL_TAS_ATMA and sira_bende:
            self.butonlar["tas_at"].config(state=tk.NORMAL)
            self.butonlar["el_ac"].config(state=tk.NORMAL)
        elif oyun_durumu == GameState.BITIS:
            self.butonlar["yeni_oyun"].config(state=tk.NORMAL)

    
    def yerden_al(self):
        self.arayuz.oyun.atilan_tasi_al(0)
        self.arayuz.arayuzu_guncelle()

    @logger.log_function
    def gec(self):
        self.arayuz.oyun.atilan_tasi_gecti()
        self.arayuz.arayuzu_guncelle()

    @logger.log_function
    def desteden_cek(self):
        self.arayuz.oyun.desteden_cek(0)
        self.arayuz.arayuzu_guncelle()

    @logger.log_function
    def el_ac(self):
        secili_idler = self.arayuz.secili_tas_idler
        if not secili_idler:
            self.arayuz.statusbar.guncelle("Lütfen açmak için taş seçin.")
            return
        sonuc = self.arayuz.oyun.el_ac(0, secili_idler)
        if sonuc.get("status") == "success":
            self.arayuz.secili_tas_idler = []
            self.arayuz.statusbar.guncelle("Per başarıyla açıldı!")
        elif sonuc.get("status") == "joker_choice_needed":
            self.arayuz.joker_secim_penceresi_ac(sonuc["options"], sonuc["joker"], sonuc["secilen_taslar"])
        else:
            self.arayuz.statusbar.guncelle(sonuc.get("message", "Geçersiz per!"))
        self.arayuz.arayuzu_guncelle()

    @logger.log_function
    def tas_at(self):
        secili = self.arayuz.secili_tas_idler
        if len(secili) == 1:
            self.arayuz.oyun.tas_at(0, secili[0])
            self.arayuz.secili_tas_idler = []
        else:
            self.arayuz.statusbar.guncelle("Lütfen atmak için sadece 1 taş seçin.")
        self.arayuz.arayuzu_guncelle()

    @logger.log_function
    def yeni_oyun(self):
        self.arayuz.oyun.baslat()
        self.arayuz.arayuzu_guncelle()