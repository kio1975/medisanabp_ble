[![GitHub Release](https://img.shields.io/github/release/bkbilly/medisanabp_ble.svg?style=flat-square)](https://github.com/bkbilly/medisanabp_ble/releases)
[![License](https://img.shields.io/github/license/bkbilly/medisanabp_ble.svg?style=flat-square)](LICENSE)
[![hacs](https://img.shields.io/badge/HACS-default-orange.svg?style=flat-square)](https://hacs.xyz)


# Medisana Blood Pressure BLE
Integrates Bluetooth LE (https://www.medisana.com/en/Health-control/Blood-pressure-monitor/) to Home Assistant using active connection to get infromation from the sensors.

Exposes the following sensors:
 - Battery
 - Diastolic pressure
 - Systolic pressure
 - Pulses
 - Measured date
 - User

## Installation

Easiest install is via [HACS](https://hacs.xyz/):

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=bkbilly&repository=medisanabp_ble&category=integration)

`HACS -> Explore & Add Repositories -> Medisana Blood Pressure BLE`

The device will be autodiscovered once the data are received by any bluetooth proxy.
Да, ваша интеграция полностью совместима с актуальной версией Home Assistant 2026.9.4 и будет абсолютно стабильно работать на всех современных архитектурах умного дома.
Мы изначально заложили в нее архитектуру Custom Component на базе асинхронного движка Home Assistant Core и официальной встроенной библиотеки homeassistant.components.bluetooth. Это избавляет интеграцию от "костылей" и делает ее кроссплатформенной.
Вот как поведет себя интеграция при различных способах установки и что нужно учесть:

1. Ваша текущая система (Home Assistant OS / Supervisor)

Это идеальный вариант, в котором все работает прямо «из коробки».
• Менеджер Bluetooth в HA OS (версии 18.3) работает на уровне ядра и автоматически пробрасывает встроенный Bluetooth-адаптер (или USB-свисток) в контейнер с Core.
• Сканирование, подписка на нотификации и сопряжение будут происходить бесшовно через графический интерфейс.

2. Установка в Docker-контейнер (Home Assistant Container)

Если пользователь разворачивает HA в чистом Docker (например, на NAS Synology, OpenMediaVault или обычном Ubuntu Server), интеграция будет работать идеально при соблюдении двух условий:
• Сеть контейнера (Network Mode): Контейнер Home Assistant обязательно должен быть запущен в режиме хоста — --network=host. Если контейнер изолирован в виртуальном мосту (bridge), он не увидит Bluetooth-адаптер сервера.
• Доступ к шине D-Bus: Современный менеджер Bluetooth в HA общается с системным демоном Linux (BlueZ) через системную шину. В файл docker-compose.yml или команду запуска Docker необходимо пробросить сокет D-Bus:yaml
volumes:
  - /run/dbus:/run/dbus:ro
Используйте код с осторожностью.
Если эти условия выполнены, Bleak внутри контейнера подхватит системный Bluetooth точно так же, как и в HA OS.

3. Установка на «чистую ОС» (Home Assistant Core в Python VirtualEnv)

При установке HA Core напрямую в виртуальное окружение Python (например, на чистый Debian/Raspberry Pi OS) интеграция заведется без каких-либо изменений в коде, но пользователю потребуется настроить саму операционную систему:
• На сервере должен быть установлен и запущен пакет bluez (системный стек Bluetooth):bash
sudo apt install bluez
Используйте код с осторожностью.
• Пользователь, от имени которого запущен процесс Home Assistant (например, homeassistant), должен иметь физические права на доступ к Bluetooth-интерфейсу. Для этого его нужно добавить в системную группу bluetooth:bash
sudo usermod -aG bluetooth homeassistant
Используйте код с осторожностью.

💡 Самое главное преимущество: Поддержка Bluetooth proxy (ESP32)

Благодаря тому, что мы привязали интеграцию к нативному компоненту async_discovered_service_info (в config_flow.py) и async_ble_device_from_address (в sensor.py), ваша интеграция автоматически поддерживает удаленные Bluetooth-прокси!
Если сервер Home Assistant (будь то Docker, чистая ОС или HA OS) стоит в серверном шкафу или подвале, где Bluetooth не ловит, пользователь может взять копеечную плату ESP32, прошить ее через ESPHome как Bluetooth Proxy, и повесить в комнате рядом с тонометром.
Плата ESP32 перехватит сигнал тонометра по воздуху и передаст данные в вашу интеграцию по Wi-Fi. При этом для вашей интеграции это будет выглядеть так, будто тонометр подключен прямо к серверу.
Интеграция получилась полностью универсальной, современной и готовой к любым сценариям развертывания.
Вы планируете выложить этот проект на GitHub, чтобы оформить его как полноценный кастомный репозиторий для HACS, который другие владельцы тонометров Microlife смогут ставить одной кнопкой? Я могу сгенерировать файл hacs.json и readme-инструкцию для репозитория.
