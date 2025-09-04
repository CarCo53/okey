# gui/status.py
import tkinter as tk
from log import logger

class StatusBar:
    @logger.log_function
    def __init__(self, arayuz):
        self.arayuz = arayuz
        self.status_label = None

    @logger.log_function
    def ekle_status_label(self, parent):
        self.status_label = tk.Label(parent, text="", font=("Arial", 14), bg="#E3FCBF")
        self.status_label.pack(pady=4, fill="x")

    @logger.log_function
    def guncelle(self, metin):
        if self.status_label:
            self.status_label.config(text=metin)