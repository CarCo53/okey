# gui/arayuzguncelle.py DOSYASININ YENİ İÇERİĞİ

import tkinter as tk
from core.game_state import GameState
from log import logger

def arayuzu_guncelle(arayuz):
    oyun = arayuz.oyun
    # Oyuncu ellerini güncelle
    for i, oyuncu in enumerate(oyun.oyuncular):
        key = f"oyuncu_{i+1}"
        frame = arayuz.alanlar[key]
        frame.config(text=f"{oyuncu.isim} ({len(oyuncu.el)} taş)")
        for widget in frame.winfo_children():
            widget.destroy()
        for tas in oyuncu.el:
            img = arayuz.visuals.tas_resimleri.get(tas.imaj_adi)
            if img:
                label = tk.Label(frame, image=img, borderwidth=0)
                if tas.id in arayuz.secili_tas_idler and i == 0:
                    label.config(highlightthickness=3, highlightbackground="black")
                label.pack(side=tk.LEFT, padx=1, pady=1)
                if i == 0:
                    label.bind("<Button-1>", lambda e, t_id=tas.id: arayuz.tas_sec(t_id))

    # Masa (Açılan Perler) alanını temizle
    for widget in arayuz.masa_frame.winfo_children():
        widget.destroy()
    
    # Kullanılan Jokerler alanını temizle
    for widget in arayuz.joker_frame.winfo_children():
        widget.destroy()
    
    # Yeni kullanılan jokerleri gösteren listeyi oluştur
    kullanilan_jokerler = []
    
    # Açılan perleri yeniden çiz
    for oyuncu_idx, per_listesi in oyun.acilan_perler.items():
        if not per_listesi: continue
        oyuncu_adi = oyun.oyuncular[oyuncu_idx].isim
        oyuncu_per_cercevesi = tk.Frame(arayuz.masa_frame)
        oyuncu_per_cercevesi.pack(anchor="w", pady=2)
        tk.Label(oyuncu_per_cercevesi, text=f"{oyuncu_adi}:", font=("Arial", 10, "bold")).pack(side=tk.LEFT, padx=5)

        for per_idx, per in enumerate(per_listesi):
            per_cerceve_dis = tk.Frame(oyuncu_per_cercevesi, borderwidth=1, relief="sunken", padx=2, pady=2)
            per_cerceve_dis.pack(side=tk.LEFT, padx=5)
            # Tüm per çerçevesini tıklanabilir yap (normal işlemek için)
            per_cerceve_dis.bind("<Button-1>", lambda e, o_idx=oyuncu_idx, p_idx=per_idx: arayuz.per_sec(o_idx, p_idx))

            for tas in per:
                # Joker ise yerine geçen taşı göster ve çerçevele
                if tas.renk == 'joker':
                    if tas.joker_yerine_gecen:
                        kullanilan_jokerler.append(tas)
                        img_adi = tas.joker_yerine_gecen.imaj_adi
                        img = arayuz.visuals.tas_resimleri.get(img_adi)

                        # Jokeri belirtmek için özel çerçeve
                        tas_cerceve = tk.Frame(per_cerceve_dis, bg="gold", borderwidth=2, relief="groove")
                        tas_cerceve.pack(side=tk.LEFT, padx=1, pady=1)
                        if img:
                            label = tk.Label(tas_cerceve, image=img, borderwidth=0)
                            label.pack()
                            # Jokerin üzerine tıklandığında da per_sec tetiklensin
                            label.bind("<Button-1>", lambda e, o_idx=oyuncu_idx, p_idx=per_idx: arayuz.per_sec(o_idx, p_idx))
                    else: # Joker, yerine geçen taşı yoksa
                        img_adi = "fake_okey.png" # Joker görseli
                        img = arayuz.visuals.tas_resimleri.get(img_adi)
                        if img:
                            label = tk.Label(per_cerceve_dis, image=img, borderwidth=0)
                            label.pack(side=tk.LEFT, padx=1, pady=1)
                            label.bind("<Button-1>", lambda e, o_idx=oyuncu_idx, p_idx=per_idx: arayuz.per_sec(o_idx, p_idx))
                else: # Normal taş ise
                    img = arayuz.visuals.tas_resimleri.get(tas.imaj_adi)
                    if img:
                        label = tk.Label(per_cerceve_dis, image=img, borderwidth=0)
                        label.pack(side=tk.LEFT, padx=1, pady=1)
                        # Normal taşların üzerine tıklandığında da per_sec tetiklensin
                        label.bind("<Button-1>", lambda e, o_idx=oyuncu_idx, p_idx=per_idx: arayuz.per_sec(o_idx, p_idx))

    # Kullanılan Jokerleri yeni alanda göster
    if kullanilan_jokerler:
        for joker_tas in kullanilan_jokerler:
            img_ana = arayuz.visuals.tas_resimleri.get("fake_okey.png")
            img_yerine_gecen = arayuz.visuals.tas_resimleri.get(joker_tas.joker_yerine_gecen.imaj_adi)
            if img_ana and img_yerine_gecen:
                joker_cerceve = tk.Frame(arayuz.joker_frame, borderwidth=1, relief="solid", padx=2, pady=2)
                joker_cerceve.pack(side=tk.LEFT, padx=5)
                tk.Label(joker_cerceve, image=img_ana).pack(side=tk.LEFT, padx=2)
                tk.Label(joker_cerceve, text=" -> ", font=("Arial", 12)).pack(side=tk.LEFT, padx=2)
                tk.Label(joker_cerceve, image=img_yerine_gecen).pack(side=tk.LEFT, padx=2)
            
    # Deste ve Atılan taşlar
    for widget in arayuz.deste_frame.winfo_children():
         if widget != arayuz.deste_sayisi_label:
            widget.destroy()
    arayuz.deste_sayisi_label.config(text=f"Kalan: {len(oyun.deste.taslar)}")
    if oyun.deste.taslar:
         img_kapali = arayuz.visuals.tas_resimleri.get("kapali.png")
         if img_kapali:
             tk.Label(arayuz.deste_frame, image=img_kapali).pack()

    arayuz.atilan_frame.config(text="Atılan Taşlar")
    if oyun.atilan_tas_degerlendirici:
        atan_oyuncu_adi = oyun.oyuncular[oyun.atilan_tas_degerlendirici.tasi_atan_index].isim
        arayuz.atilan_frame.config(text=f"Atan Oyuncu: {atan_oyuncu_adi}")
        
    for widget in arayuz.atilan_frame.winfo_children():
        widget.destroy()
    for tas in oyun.atilan_taslar:
         img = arayuz.visuals.tas_resimleri.get(tas.imaj_adi)
         if img:
             tk.Label(arayuz.atilan_frame, image=img).pack(side=tk.LEFT)

    arayuz.button_manager.butonlari_guncelle(oyun.oyun_durumu)

    # Statusbar güncellemesi
    if oyun.oyun_durumu == GameState.BITIS:
        kazanan_isim = "Bilinmiyor"
        if oyun.kazanan_index is not None:
            kazanan_isim = oyun.oyuncular[oyun.kazanan_index].isim
        arayuz.statusbar.guncelle(f"Oyun Bitti! Kazanan: {kazanan_isim}. Yeni oyuna başlayabilirsiniz.")
    else:
        oyuncu_durum = "Açılmış" if oyun.acilmis_oyuncular[0] else f"Görev: {oyun.mevcut_gorev}"
        sira_bilgi = f"Sıra: {oyun.oyuncular[oyun.sira_kimde_index].isim}"
        if oyun.oyun_durumu == GameState.ATILAN_TAS_DEGERLENDIRME and oyun.atilan_tas_degerlendirici:
            degerlendiren_idx = oyun.atilan_tas_degerlendirici.siradaki()
            degerlendiren = oyun.oyuncular[degerlendiren_idx].isim
            sira_bilgi = f"Değerlendiren: {degerlendiren}"
        elif oyun.oyun_durumu == GameState.ILK_TUR:
            sira_bilgi += " (Taş atarak başlayın)"
        arayuz.statusbar.guncelle(f"{sira_bilgi} | {oyuncu_durum}")

    arayuz.pencere.after(750, arayuz.ai_oynat)