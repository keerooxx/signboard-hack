import os
import time
import subprocess
import json
import sys
import hashlib
import requests
import re
from threading import Thread
import getpass
import shutil

# ===== ОБНОВЛЕННАЯ КОНФИГУРАЦИЯ =====
# ... [ваш список TARGET_PREFIXES] ...
# ... [ваш PASSWORD_LIST] ...
SCAN_INTERVAL = 15
PASSWORD = "k33rooxx"
REPO_URL = "https://raw.githubusercontent.com/keerooxx/signboard-hack/main/scanner.py"
VERSION = "1.4"
# ========================

def print_banner():
    print(r"""
 ██ ▄█▀▓█████  ██▀███   ▒█████  ▒██   ██▒
 ██▄█▒ ▓█   ▀ ▓██ ▒ ██▒▒██▒  ██▒▒▒ █ █ ▒░
▓███▄░ ▒███   ▓██ ░▄█ ▒▒██░  ██▒░░  █   ░
▓██ █▄ ▒▓█  ▄ ▒██▀▀█▄  ▒██   ██░ ░ █ █ ▒ 
▒██▒ █▄░▒████▒░██▓ ▒██▒░ ████▓▒░▒██▒ ▒██▒
▒ ▒▒ ▓▒░░ ▒░ ░░ ▒▓ ░▒▓░░ ▒░▒░▒░ ▒▒ ░ ░▓ ░
░ ░▒ ▒░ ░ ░  ░  ░▒ ░ ▒░  ░ ▒ ▒░ ░░   ░▒ ░
░ ░░ ░    ░     ░░   ░ ░ ░ ░ ▒   ░    ░  
░  ░      ░  ░   ░         ░ ░   ░    ░  
    """)
    print(f"Wi-Fi Scanner Tool | by @krx1krx | v{VERSION}")
    print("="*45)

def auto_update():
    try:
        print("[~] Проверка обновлений...")
        response = requests.get(REPO_URL + "?t=" + str(time.time()))
        if response.status_code != 200:
            print(f"[!] Ошибка проверки обновлений: {response.status_code}")
            return False
        
        current_hash = hashlib.md5(open(__file__, 'rb').read()).hexdigest()
        new_hash = hashlib.md5(response.content).hexdigest()
        
        if current_hash == new_hash:
            print("[✓] У вас последняя версия скрипта")
            return False
        
        print("[~] Найдено обновление, устанавливаем...")
        with open(__file__, 'wb') as f:
            f.write(response.content)
        
        print("[✓] Скрипт успешно обновлен!")
        print("[~] Перезапускаю скрипт...")
        os.execv(sys.executable, [sys.executable] + sys.argv)
        return True
        
    except Exception as e:
        print(f"[!] Ошибка обновления: {e}")
        return False

def install_dependencies():
    """Автоматическая установка зависимостей"""
    try:
        print("[~] Установка необходимых компонентов...")
        
        # Обновление пакетов
        subprocess.run(["pkg", "update", "-y"], check=True)
        
        # Установка Termux API
        subprocess.run(["pkg", "install", "termux-api", "-y"], check=True)
        
        print("[✓] Компоненты Termux успешно установлены!")
        print("[~] Установите приложение Termux:API через F-Droid:")
        print("    1. Установите F-Droid: https://f-droid.org")
        print("    2. Найдите 'Termux:API' в F-Droid")
        print("    3. Установите приложение")
        print("[~] Предоставьте разрешения для Termux:API")
        print("[~] Перезапустите Termux и запустите скрипт снова")
        
        return True
    except Exception as e:
        print(f"[!] Ошибка установки: {e}")
        print("[!] Установите зависимости вручную:")
        print("    pkg install termux-api")
        return False

def check_termux_api_installed():
    """Проверка установлен ли Termux:API"""
    return shutil.which("termux-wifi-scan") and shutil.which("termux-wifi-connect")

def main():
    # Проверка обновлений
    if "--no-update" not in sys.argv and "--restarted" not in sys.argv:
        if auto_update():
            return
    
    if "--restarted" not in sys.argv:
        sys.argv.append("--restarted")
    
    print_banner()
    
    # Проверка зависимостей
    if not check_termux_api_installed():
        print("[!] Termux API не установлен!")
        print("\n[?] Попробовать установить автоматически? (y/n)")
        choice = input().strip().lower()
        
        if choice == 'y':
            if install_dependencies():
                print("[✓] Зависимости установлены. Перезапустите скрипт.")
            else:
                print("[!] Не удалось установить зависимости")
            return
        else:
            print("\n[!] Установите зависимости вручную:")
            print("    pkg install termux-api")
            print("[!] И установите приложение Termux:API через F-Droid")
            print("    Ссылка: https://f-droid.org/packages/com.termux.api/")
            return
    
    # ... [остальная часть main без изменений] ...

if __name__ == "__main__":
    main()
