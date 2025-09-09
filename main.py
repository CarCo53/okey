# main.py
import sys
import os
import argparse
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from engine.game_manager import Game
from gui.gui import Arayuz
from rules.gorevler import GOREV_LISTESI
from log import logger

@logger.log_function
def main():
    parser = argparse.ArgumentParser(description="Okey Oyunu")
    parser.add_argument("-gorev", type=str, choices=GOREV_LISTESI, help="Oyunun başlayacağı özel görevi belirler.")
    args = parser.parse_args()

    oyun = Game()
    oyun.baslat(args.gorev)
    gui = Arayuz(oyun)
    gui.baslat()

if __name__ == "__main__":
    main()