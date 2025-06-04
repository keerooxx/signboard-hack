# Wi-Fi Scanner для вывесок

Скрипт для автоматического обнаружения Wi-Fi вывесок в Termux

## Установка
```bash
pkg update -y
pkg install git python termux-api -y
pip install requests
git clone https://github.com/ваш_логин/ваш_репозиторий.git
cd ваш_репозиторий
python scanner.py