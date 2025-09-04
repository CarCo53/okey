# main.py
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from engine.game_manager import Game
from gui.gui import Arayuz

if __name__ == "__main__":
    oyun = Game()
    oyun.baslat()
    gui = Arayuz(oyun)
    gui.baslat()