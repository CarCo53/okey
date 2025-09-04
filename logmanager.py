import os
import argparse
import re

# --- AYARLAR ---
DECORATOR_LINE = "@logger.log_function"
IMPORT_LINE = "from log import logger"
FILES_TO_IGNORE = [os.path.basename(__file__), 'log.py']

# Gürültü yaptığı için loglanmayacak fonksiyonların "kara listesi"
FUNCTIONS_TO_IGNORE = [
    'Arayuz.ai_oynat',
    'Game.oyun_bitti_mi',
]
# --- AYARLAR ---

def find_py_files(start_path='.'):
    py_files = []
    for root, _, files in os.walk(start_path):
        for file in files:
            if file.endswith('.py') and file not in FILES_TO_IGNORE:
                py_files.append(os.path.join(root, file))
    return py_files

def get_indent(line):
    return re.match(r"\s*", line).group(0)

def process_file(filepath, action):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except Exception as e:
        print(f"HATA: {filepath} dosyası okunamadı - {e}")
        return

    original_line_count = len(lines)
    new_lines = []
    
    if action == 'sil':
        new_lines = [line for line in lines if DECORATOR_LINE not in line and IMPORT_LINE not in line]
        if len(new_lines) == original_line_count:
            print(f"BİLGİ: Kaldırılacak log bulunamadı -> {filepath}")
            return
    
    elif action == 'ekle':
        current_class = None
        import_exists = any(IMPORT_LINE in line for line in lines)
        
        # Önceki logları temizle, temiz bir başlangıç yap
        lines = [line for line in lines if DECORATOR_LINE not in line]
        
        for line in lines:
            stripped_line = line.strip()
            
            if stripped_line.startswith('class '):
                current_class = stripped_line.split(' ')[1].split('(')[0].replace(':', '')

            if stripped_line.startswith('def '):
                func_name = stripped_line.split(' ')[1].split('(')[0]
                full_func_name = f"{current_class}.{func_name}" if current_class else func_name
                
                if full_func_name in FUNCTIONS_TO_IGNORE:
                    new_lines.append(line)
                    print(f"BİLGİ: '{full_func_name}' kara listede, atlanıyor.")
                    continue

                indent = get_indent(line)
                new_lines.append(f"{indent}{DECORATOR_LINE}\n")
            
            new_lines.append(line)

        if not import_exists and any(DECORATOR_LINE in l for l in new_lines):
            # Eğer log eklendiyse ve import yoksa, ekle
            last_import_index = -1
            for i, line in enumerate(new_lines):
                if line.strip().startswith(('import ', 'from ')):
                    last_import_index = i
            
            if last_import_index != -1:
                new_lines.insert(last_import_index + 1, f"{IMPORT_LINE}\n")
            else:
                new_lines.insert(0, f"{IMPORT_LINE}\n")

    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.writelines(new_lines)
        if len(new_lines) != original_line_count:
            status = "eklendi" if action == "ekle" else "kaldırıldı"
            print(f"BAŞARILI: Loglar {status} -> {filepath}")

    except Exception as e:
        print(f"HATA: {filepath} dosyasına yazılamadı - {e}")

def main():
    parser = argparse.ArgumentParser(description="Projedeki Python dosyalarına loglama ekler veya kaldırır.")
    parser.add_argument('action', choices=['ekle', 'sil'], help="'ekle' veya 'sil' komutunu kullanın.")
    args = parser.parse_args()
    
    files_to_process = find_py_files()
    
    if args.action == 'ekle':
        print("\n--- Loglama Ekleniyor ---")
        for filepath in files_to_process:
            process_file(filepath, 'ekle')
    elif args.action == 'sil':
        print("\n--- Loglama Kaldırılıyor ---")
        for filepath in files_to_process:
            process_file(filepath, 'sil')
    print("\nİşlem tamamlandı.")

if __name__ == "__main__":
    main()