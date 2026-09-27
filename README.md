# Практическая работа №1: музыкальный плеер

Кольцевой двусвязный список `LinkedList`, узлы `LinkedListItem`, композиции
`Composition` и наследующий список `PlayList`. Интерфейс — Tkinter;
воспроизведение WAV, MP3 и OGG — pygame-ce (импортируется как `pygame`).

## Запуск исходников: Windows и Linux

Нужен Python 3.11 или новее. Выполняйте команды из папки репозитория.

```sh
python -m pip install -r requirements.txt
python app.py
```

В Ubuntu/Debian при отсутствии Tkinter и для создания виртуального окружения:

```sh
sudo apt install python3-tk python3-venv
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python app.py
```

Запускайте приложение в графическом сеансе с доступным аудиоустройством.
В Windows можно также открыть `music_player.exe`: Python и установка зависимостей
для EXE не нужны. EXE предназначен только для Windows; в Linux запускайте `app.py`.

## Использование

Создайте плейлист, добавьте файлы, выделите композицию и нажмите «Воспроизвести».
Кнопки «Выше» и «Ниже» меняют порядок; «Удалить» удаляет выбранный трек или
плейлист. Есть запуск следующей и предыдущей композиции. По завершении трека
автоматически запускается следующий; после последнего — первый.
Смена плейлиста и редактирование порядка останавливают музыку.
Плейлисты хранятся в памяти до закрытия приложения.

## Проверки

```sh
python -m unittest discover -v
python -m pip install pylint==4.0.8
python -m pylint --rcfile=.pylintrc app.py linked_list.py test_linked_list.py test_audio.py
```

`.pylintrc` — файл настроек проверки кода. `requirements.txt` — зависимости
для запуска; `test_*.py` — автоматические тесты. Аудиотест использует виртуальное
устройство SDL и не требует колонок.
