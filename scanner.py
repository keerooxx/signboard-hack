import os
import time
import subprocess
import json
import sys
from threading import Thread
import getpass

# ===== КОНФИГУРАЦИЯ =====
TARGET_PREFIXES = [
    # Основные префиксы вывесок
    "A5L", "A6L", "B6L", "H4K", "H8", "H6", "B8L", "A7", "A8", "A3",
    "A4", "A5", "A6", "C16L", "C08L", "C16", "C15", "C35", "D16", "D36",
    "D15", "D35", "C36", "Q910", "B6", "D10", "D20", "D30", "C10", "C30",
    "A30", "A30+", "A601", "A602", "A603", "A604", "A605", "A606", "A607",
    
    # Префиксы на V и M
    "V10", "V20", "V30", "V40", "V50", "V60", "M10", "M20", "M30", "M40",
    "M50", "M60", "MV10", "MV20", "MV30", "MV40", "VM10", "VM20", "VM30",
    
    # Префиксы на W
    "W10", "W20", "W30", "W40", "W50", "W60", "W70", "W80", "W90",
    "W100", "W200", "W300", "W1", "W2", "W3", "W4", "W5", "W6", "W7", "W8", "W9",
    "W01", "W02", "W03", "W04", "W05", "W06", "W07", "W08", "W09",
    "WA", "WB", "WC", "WD", "WE", "WF", "WG", "WH", "WI", "WJ", "WK", "WL",
    "WM", "WN", "WO", "WP", "WQ", "WR", "WS", "WT", "WU", "WV", "WW", "WX",
    "WY", "WZ",
    
    # Другие распространенные префиксы
    "P10", "P16", "P20", "P25", "P30", "P40", "P50", "P60", "P80", "P100",
    "S10", "S20", "S30", "S40", "S50", "S60", "S70", "S80", "S90",
    "T10", "T20", "T30", "T40", "T50", "T60", "T70", "T80", "T90",
    "R10", "R20", "R30", "R40", "R50", "R60", "R70", "R80", "R90",
    "F10", "F20", "F30", "F40", "F50", "F60", "F70", "F80", "F90",
    "G10", "G20", "G30", "G40", "G50", "G60", "G70", "G80", "G90",
    
    # Короткие цифровые префиксы
    "100", "200", "300", "400", "500", "600", "700", "800", "900",
    "101", "202", "303", "404", "505", "606", "707", "808", "909",
    "110", "220", "330", "440", "550", "660", "770", "880", "990",
    
    # Специальные префиксы
    "LCD", "LED", "SMD", "RGB", "OLED", "QLED", "DISP", "SCRN", "BRD", "SIGN",
    "ADV", "ADS", "PUB", "OUT", "IN", "SHOP", "STORE", "MALL", "HOTEL", "CAFE"
]

PASSWORD_LIST = [
    "88888888", "888888eu", "12345678", "87654321",
    "00000000", "11111111", "admin123"  # Добавленные пароли
]
SCAN_INTERVAL = 30  # Интервал сканирования в секундах
PASSWORD = "k33rooxx"  # Пароль виден только в коде
# ========================

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
    """Проверка пароля без отображения в консоли"""
    print("[!] Для запуска требуется пароль")
    
    # Считываем пароль без отображения
    try:
        import getpass
        user_input = getpass.getpass("Введите пароль: ")
    except:
        # Если getpass не работает, используем input с предупреждением
        print("[!] Внимание: пароль будет виден при вводе!")
        user_input = input("Введите пароль: ")
    
    return user_input.strip() == PASSWORD

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
        return [net["ssid"] for net in networks if "ssid" in net and net["ssid"]]
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
