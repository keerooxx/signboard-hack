# Wi-Fi Scanner для вивісок

Скрипт для автоматичного знаходження  Wi-Fi вивісок в Termux

## Установка
```bash
pkg update -y
pkg install git python termux-api -y
pip install requests
git clone https://github.com/keerooxx/signboard-hack.git
cd signboard_hack
python scanner.py
