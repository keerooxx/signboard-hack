import os
import time
import subprocess
import json
import sys
import hashlib
from threading import Thread
import getpass

# ===== КОНФИГУРАЦИЯ =====
TARGET_PREFIXES = [
    "A5L", "A6L", "B6L", "H4K", "H8", "H6", "B8L", "A7", "A8", "A3",
    "A4", "A5", "A6", "C16L", "C08L", "C16", "C15", "C35", "D16", "D36",
    "D15", "D35", "C36", "Q910", "B6", "D10", "D20", "D30", "C10", "C30",
    "A30", "A30+", "A601", "A602", "A603",
    "V10", "D05", "D06", "QF4", "LCD", "3399F", "3568S", "3568SC",
    "3568V", "3588V", "M20", "3288SC", "3566S", "3566MV", "3566P", "972S",
    "982V", "133T", "133TE", "133M", "M8D", "811V", "352C", "527S",
    "528M", "527A", "133MC", "3576V", "40S", "M30", "M10"
]

PASSWORD_LIST = ["88888888", "888888eu", "12345678", "87654321"]
SCAN_INTERVAL = 30  # Интервал сканирования в секундах
# ========================


PASSWORD_HASH = "e5e8c0d8b0f2f7d6b5c4e3f2a1b0c9d8e"  
SALT = "keerooxx_salt"

def print_keerooxx():
    """Печатаем красивый ASCII-арт для keerooxx"""
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

def check_password():
    """Проверяем пароль"""
    try:
        password = getpass.getpass("Введите пароль: ")
        # Проверка пароля через хеширование
        hashed_input = hashlib.md5((password + SALT).encode()).hexdigest()
        return hashed_input == PASSWORD_HASH
    except:
        return False

def install_dependencies():
    """Устанавливаем необходимые зависимости в Termux"""
    try:
        print("[~] Проверяем зависимости...")
        # Проверяем установлен ли termux-api
        result = subprocess.run(["termux-wifi-scaninfo"], 
                               capture_output=True, 
                               text=True)
        if "command not found" in result.stderr:
            print("[~] Устанавливаем Termux API...")
            subprocess.run(["pkg", "install", "termux-api", "-y"], check=True)
        
        print("[✓] Все зависимости установлены")
        return True
    except Exception as e:
        print(f"[!] Ошибка установки зависимостей: {e}")
        print("[!] Попробуйте выполнить вручную:")
        print("    pkg update && pkg upgrade -y")
        print("    pkg install termux-api python -y")
        return False

def get_location():
    """Получаем примерное местоположение по IP"""
    try:
        import requests
        response = requests.get('https://ipinfo.io/json', timeout=5)
        data = response.json()
        city = data.get('city', 'Unknown')
        region = data.get('region', 'Unknown')
        return f"{city}, {region}"
    except:
        return "Неизвестное местоположение"

def scan_wifi():
    """Сканируем Wi-Fi сети в Termux"""
    try:
        result = subprocess.check_output(
            ["termux-wifi-scaninfo"],
            text=True,
            stderr=subprocess.DEVNULL,
            timeout=30
        )
        return result
    except subprocess.TimeoutExpired:
        print("[!] Таймаут сканирования Wi-Fi")
        return ""
    except Exception as e:
        print(f"[!] Ошибка сканирования: {e}")
        return ""

def parse_networks(scan_result):
    """Парсим результат сканирования сетей"""
    try:
        networks = json.loads(scan_result)
        return [net["ssid"] for net in networks if "ssid" in net]
    except:
        return []

def is_target_network(ssid):
    """Проверяем, начинается ли SSID на целевой префикс"""
    return any(ssid.startswith(prefix) for prefix in TARGET_PREFIXES)

def hack_network(ssid):
    """Эмулируем процесс взлома сети"""
    print(f"\n[+] Найдена вывеска: {ssid}")
    print(f"[!] Начинаю подбор пароля...")
    time.sleep(1)
    
    for password in PASSWORD_LIST:
        print(f"    [>] Пробую: {password}")
        time.sleep(0.3)
    
    print(f"\n[!] УСПЕХ! Возможные пароли для {ssid}:")
    for password in PASSWORD_LIST:
        print(f"    • {password}")
    
    # Звуковое уведомление
    try:
        subprocess.run(["termux-beep", "-f", "1000", "-d", "500"], timeout=5)
    except:
        pass
    return True

def main():
    # Печатаем логотип
    print_keerooxx()
    print("Wi-Fi Scanner Tool | Termux Edition")
    print("Telegram: @krx1krx")
    print("======================================")
    
    # Проверка пароля
    if not check_password():
        print("[!] Неверный пароль! Доступ запрещен.")
        return
    
    print("[✓] Вход выполнен успешно")
    print("[*] Режим: пассивное сканирование")
    
    # Устанавливаем зависимости
    if not install_dependencies():
        print("[!] Продолжаем с ограниченной функциональностью")
    
    # Получаем местоположение
    try:
        location = get_location()
        print(f"[*] Ваше местоположение: {location}")
    except:
        print("[*] Не удалось определить местоположение")
    
    print(f"[*] Ищем вывески ({len(TARGET_PREFIXES)} префиксов)")
    print(f"[*] Тестируемые пароли: {', '.join(PASSWORD_LIST)}")
    print("\n[!] Нажмите Ctrl+C для остановки\n")
    
    # Звуковой сигнал старта
    try:
        subprocess.run(["termux-beep"], timeout=5)
    except:
        pass
    
    try:
        while True:
            scan_result = scan_wifi()
            if not scan_result:
                print("[~] Повторное сканирование через 10 секунд...")
                time.sleep(10)
                continue
                
            networks = parse_networks(scan_result)
            unique_networks = list(set(networks))  # Удаляем дубликаты
            target_found = False
            
            print(f"\n[~] Сканирование... Найдено сетей: {len(unique_networks)}")
            
            for ssid in unique_networks:
                if ssid and is_target_network(ssid):
                    target_found = True
                    # Запускаем процесс "взлома" в отдельном потоке
                    Thread(target=hack_network, args=(ssid,), daemon=True).start()
            
            if not target_found:
                print("    [✗] Вывесок не найдено...")
            
            time.sleep(SCAN_INTERVAL)
    except KeyboardInterrupt:
        print("\n[!] Программа остановлена")

if __name__ == "__main__":
    main()
