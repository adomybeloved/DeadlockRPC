<p align="center">
  <img src="https://github.com/user-attachments/assets/6d562252-a7e6-44ab-bfeb-8a753469b117" width="700">
</p>
<p align="center">
  <a href="https://github.com/qwertyquerty/pypresence">
    <img src="https://img.shields.io/badge/using-pypresence-00bb88?style=flat-square&logo=discord">
  </a>
  <img src="https://img.shields.io/badge/platform-Windows%20%26%20Linux-lightgrey?style=flat-square">
  <img src="https://img.shields.io/github/downloads/adomybeloved/DeadlockRPC/total?style=flat-square">
  <img src="https://img.shields.io/badge/license-GPL--3.0-blue?style=flat-square">
</p>
<p align="center">
Discord Rich Presence для
<a href="https://store.steampowered.com/app/1422450/Deadlock/">Deadlock</a> от Valve.
Показывает ваш игровой статус в Discord-профиле в реальном времени —
герой, режим игры, тип матча, размер группы, таймер матча и многое другое. Поддерживает все игровые режимы!
</p>
<p align="center">
  <img src="https://github.com/user-attachments/assets/bb411785-66f4-43ce-8c9e-d979f6ca7e96" height="135">
  <img src="https://github.com/user-attachments/assets/1d872c8d-a10f-4807-89ea-3f5327471e4b" height="135">
  <img src="https://github.com/user-attachments/assets/52f40fe4-fd2a-4abf-b404-280c84a50d8e" height="135">
  <img src="https://github.com/user-attachments/assets/112f40b9-d8d4-40f2-afa1-9f950a7ab438" height="135">
</p>

> [!NOTE]
> Этот проект является форком [Deadlock-Rich-Presence](https://github.com/Jelloge/Deadlock-Rich-Presence) от **Jelloge**.
> Оригинальный автор проделал всю основную работу — спасибо ему за это!
> Данный форк добавляет полную систему локализации (русский/английский), русские имена героев со
> склонениями, переработанный лейаут Discord-статуса и другие улучшения.

## Установка

### Windows
1. Скачайте **DeadlockRPC-windows-x86_64.zip** из [последнего релиза](https://github.com/adomybeloved/DeadlockRPC/releases/latest)
2. Распакуйте и запустите **DeadlockRPC.exe** — приложение появится в системном трее

### Linux
1. Скачайте **DeadlockRPC-linux-x86_64.zip** из [последнего релиза](https://github.com/adomybeloved/DeadlockRPC/releases/latest)
2. Распакуйте и запустите:
```bash
unzip DeadlockRPC-linux-x86_64.zip
cd DeadlockRPC
chmod +x DeadlockRPC
./DeadlockRPC
```
Убедитесь, что `-condebug` указан в параметрах запуска Deadlock в Steam (приложению нужен `console.log` для отслеживания состояния игры).

### Примечания
- Приложение автоматически проверяет обновления при запуске и предлагает обновиться, если доступна новая версия.
- По умолчанию приложение запускает Deadlock с `-condebug` автоматически через Steam.
- Если вы управляете параметрами запуска Steam самостоятельно, установите `"launch_game": false` в `config.json` и добавьте `-condebug` вручную:
<img width="480" height="119" alt="Параметры запуска Steam" src="https://github.com/user-attachments/assets/21aaf748-3f15-41de-9479-d48b3b8eba6d" />

### Локализация

Приложение поддерживает **русский** и **английский** языки. Для переключения измените поле `"language"` в `config.json`:

```json
{
    "language": "ru"
}
```

На русском языке:
- Все режимы игры отображаются по-русски (Стандартный, Рейтинговый, и т.д.)
- Имена героев — официальные русские названия от Valve (Инфернус, Пелена, Заточка...)
- Правильные склонения: «Играет за **Виндикту**», «Играет за **Серого Когтя**»
- Тексты убежища переведены (Мешает Коктейли в Убежище, Философствует в Убежище...)

<details>
<summary>Запуск из исходников</summary>

Если вы предпочитаете запускать из исходного кода:

```bash
git clone https://github.com/adomybeloved/DeadlockRPC.git
cd DeadlockRPC
pip install -r requirements.txt
cd src
python main.py
```

Требуется Python 3.10+. Для сборки standalone-исполняемого файла:
```bash
pip install pyinstaller
python build.py
```
Результат: `dist/DeadlockRPC.exe` (Windows) или `dist/DeadlockRPC` (Linux)

</details>

## Как это работает

DeadlockRPC отслеживает файл `console.log` игры Deadlock (создаётся при запуске с `-condebug`). Приложение парсит события лога с помощью регулярных выражений, определяет изменения состояния игры и отправляет обновления в Discord.

Память и рантайм игры **не затрагиваются**. Безопасно для VAC и не влияет на производительность.

## Дисклеймер

Ваш антивирус **может** пометить это приложение как вредоносное. Это известная проблема исполняемых файлов, собранных с PyInstaller, который упаковывает Python-приложения в standalone .exe файлы. Если вас беспокоит детект — вы можете собрать приложение из исходников!

## Изменения (этого форка)

- **Локализация** — полная система локализации на YAML. Русский и английский языки, включая имена героев, режимы, интерфейс трея и все сообщения
- **Русские имена героев** — официальные названия от Valve с правильными склонениями (винительный падеж)
- **Переработанный лейаут RPC** — герой отображается на второй строке, большая картинка показывает имя героя, маленькая — название игры
- **Кнопка GitHub** — в Discord-статусе отображается кнопка со ссылкой на репозиторий

## Оригинальные фичи

- **Авто-обновление** — приложение проверяет GitHub на новые релизы при запуске
- **Поддержка Linux** — полная поддержка через Proton
- **Динамические данные героев** — интеграция с `deadlock-api.com`, новые герои подхватываются автоматически
- **Текст убежища** — уникальный текст для каждого героя в убежище
- **Отслеживание группы** — реальный размер группы через GC party events
- **Определение пути Steam** — поиск Deadlock через реестр Windows

## Известные баги

Пожалуйста, создайте issue если обнаружите какие-либо баги.

## Благодарности

- **[Jelloge](https://github.com/Jelloge)** — автор оригинального проекта [Deadlock-Rich-Presence](https://github.com/Jelloge/Deadlock-Rich-Presence)
- **[pypresence](https://github.com/qwertyquerty/pypresence)** — библиотека для Discord RPC
- **[deadlock-api.com](https://deadlock-api.com)** — API для данных героев