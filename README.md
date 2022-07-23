# **@HOMEWORK_AUTOBOT**

### Описание
Telegram-бот для оповещения об изменении статуса проверки (review) домашней работы Яндекс.Практикум.<br/>
Раз в 10 минут бот делает запрос к API https://practicum.yandex.ru/api/ и в случае изменения статуса, либо возникновении неполадок отправляет соответствующее письмо в Telegram.<br/>
Для корректной работы бота необходимы токены Практикума и Telegram, а также ID чата в Telegram, куда будут отправляться сообщения.
У API Практикум.Домашка есть лишь один эндпоинт:<br/>
https://practicum.yandex.ru/api/user_api/homework_statuses/

### **Стек**
![python version](https://img.shields.io/badge/Python-3.7-green)
![python-dotenv version](https://img.shields.io/badge/dotenv-0.19-green)
![python-telegram-bot version](https://img.shields.io/badge/telegrambot-13.7-green)
![pytest version](https://img.shields.io/badge/pytest-6.2-green)
![requests version](https://img.shields.io/badge/requests-2.26-green)

### **Запуск проекта в dev-режиме**
Инструкция ориентирована на операционную систему windows и утилиту git bash.<br/>
Для прочих инструментов используйте аналоги команд для вашего окружения.

1. Клонируйте репозиторий и перейдите в него в командной строке:

```
git clone https://github.com/Banes31/homework_bot.git
```

```
cd homework_bot
```

2. Установите и активируйте виртуальное окружение
```
python -m venv venv
``` 
```
source venv/Scripts/activate
```

3. Установите зависимости из файла requirements.txt
```
pip install -r requirements.txt
```

4. В консоле импортируйте токены для Яндекс.Практикум и Телеграмм:
```bash
export PRACTICUM_TOKEN=<PRACTICUM_TOKEN>
export TELEGRAM_TOKEN=<TELEGRAM_TOKEN>
export CHAT_ID=<CHAT_ID>
```

5. Запустите бота, выполнив команду:
```bash
python homework.py
```

6. Деактивируйте виртуальное окружение (после работы), выполнив команду:
```bash
deactivate
```

### **Автор**
[Иван Зоренко](https://github.com/Banes31)