# gui/visuals.py
import os
from PIL import Image, ImageTk
from log import logger

class Visuals:
    @logger.log_function
    def __init__(self):
        self.tas_resimleri = {}

    @logger.log_function
    def yukle(self, images_path="images", boyut=(40, 60)):
        for dosya in os.listdir(images_path):
            if dosya.endswith(".png"):
                tam_yol = os.path.join(images_path, dosya)
                try:
                    img = Image.open(tam_yol)
                    img = img.resize(boyut, Image.Resampling.LANCZOS)
                    self.tas_resimleri[dosya] = ImageTk.PhotoImage(img)
                except Exception as e:
                    print(f"Görsel yüklenemedi: {tam_yol} ({e})")