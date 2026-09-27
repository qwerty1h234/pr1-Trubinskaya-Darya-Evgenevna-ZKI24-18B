"""Графический интерфейс простого музыкального плеера."""

from __future__ import annotations

import os
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog, ttk
from typing import Dict, Optional

from pygame import mixer
from pygame.base import error as AudioError

from linked_list import Composition, PlayList


class AudioPlayer:
    """Воспроизводит WAV, MP3 и OGG через SDL на Windows и Linux."""

    def __init__(self) -> None:
        """Отложить открытие аудиоустройства до первого воспроизведения."""
        self._started = False

    def play(self, composition: Composition) -> None:
        """Запустить файл; ошибки устройства и декодера передать интерфейсу."""
        if not os.path.isfile(composition.path):
            raise FileNotFoundError("Музыкальный файл не найден")
        self.stop()
        if not mixer.get_init():
            mixer.init()
        mixer.music.load(composition.path)
        mixer.music.play()
        self._started = True

    def is_playing(self) -> bool:
        """Проверить фактическое состояние воспроизведения."""
        return self._started and mixer.music.get_busy()

    def stop(self) -> None:
        """Остановить воспроизведение."""
        if mixer.get_init():
            mixer.music.stop()
            mixer.music.unload()
        self._started = False


class PlayerApplication(tk.Tk):
    """Окно управления несколькими плейлистами."""

    def __init__(self) -> None:
        """Построить интерфейс и создать первый плейлист."""
        super().__init__()
        self.title("Связный плеер")
        self.minsize(680, 390)
        self.playlists: Dict[str, PlayList] = {"Мой плейлист": PlayList()}
        self.audio = AudioPlayer()
        self._play_token = 0
        self._build_interface()
        self._refresh_playlists()
        self.protocol("WM_DELETE_WINDOW", self._close)

    def _build_interface(self) -> None:
        """Разместить элементы управления."""
        main = ttk.Frame(self, padding=14)
        main.pack(fill=tk.BOTH, expand=True)
        main.columnconfigure(1, weight=1)
        main.rowconfigure(1, weight=1)
        ttk.Label(main, text="Плейлисты").grid(row=0, column=0, sticky="w")
        ttk.Label(main, text="Композиции").grid(row=0, column=1, sticky="w", padx=(12, 0))
        self.playlist_box = tk.Listbox(main, exportselection=False, width=24)
        self.playlist_box.grid(row=1, column=0, sticky="nsew")
        self.playlist_box.bind("<<ListboxSelect>>", lambda _: self._select_playlist())
        self.track_box = tk.Listbox(main, exportselection=False)
        self.track_box.grid(row=1, column=1, sticky="nsew", padx=(12, 0))
        playlist_buttons = ttk.Frame(main)
        playlist_buttons.grid(row=2, column=0, sticky="ew", pady=(8, 0))
        ttk.Button(playlist_buttons, text="Создать", command=self._create_playlist).pack(side=tk.LEFT)
        ttk.Button(playlist_buttons, text="Удалить", command=self._delete_playlist).pack(side=tk.LEFT, padx=5)
        track_buttons = ttk.Frame(main)
        track_buttons.grid(row=2, column=1, sticky="ew", padx=(12, 0), pady=(8, 0))
        ttk.Button(track_buttons, text="Добавить файл", command=self._add_track).pack(side=tk.LEFT)
        ttk.Button(track_buttons, text="Удалить", command=self._delete_track).pack(side=tk.LEFT, padx=5)
        ttk.Button(track_buttons, text="Выше", command=lambda: self._move_track(-1)).pack(side=tk.LEFT)
        ttk.Button(track_buttons, text="Ниже", command=lambda: self._move_track(1)).pack(side=tk.LEFT, padx=5)
        controls = ttk.Frame(main)
        controls.grid(row=3, column=0, columnspan=2, pady=(16, 0))
        ttk.Button(controls, text="Предыдущий", command=self._previous).pack(side=tk.LEFT)
        ttk.Button(controls, text="Воспроизвести", command=self._play_selected).pack(side=tk.LEFT, padx=5)
        ttk.Button(controls, text="Следующий", command=self._next).pack(side=tk.LEFT)
        ttk.Button(controls, text="Стоп", command=self._stop).pack(side=tk.LEFT, padx=5)
        self.status = tk.StringVar(value="Выберите композицию")
        ttk.Label(main, textvariable=self.status).grid(
            row=4, column=0, columnspan=2, sticky="w", pady=(12, 0)
        )

    def _selected_playlist(self) -> Optional[PlayList]:
        """Вернуть выделенный плейлист."""
        selection = self.playlist_box.curselection()
        return self.playlists.get(self.playlist_box.get(selection[0])) if selection else None

    def _select_playlist(self) -> None:
        """Остановить старый плейлист при выборе другого."""
        self._stop()
        self._refresh_tracks()

    def _close(self) -> None:
        """Освободить аудиоустройство и закрыть окно."""
        self._stop()
        mixer.quit()
        self.destroy()

    def _refresh_playlists(self, selected: Optional[str] = None) -> None:
        """Обновить список плейлистов, сохранив выделение."""
        self._stop()
        self.playlist_box.delete(0, tk.END)
        for name in self.playlists:
            self.playlist_box.insert(tk.END, name)
        if self.playlists:
            names = list(self.playlists)
            index = names.index(selected) if selected in names else 0
            self.playlist_box.selection_set(index)
        self._refresh_tracks()

    def _refresh_tracks(self, selected: Optional[int] = None) -> None:
        """Показать композиции выбранного плейлиста."""
        self.track_box.delete(0, tk.END)
        playlist = self._selected_playlist()
        if playlist is None:
            return
        for node in playlist:
            self.track_box.insert(tk.END, node.data.title)
        if selected is not None and selected < len(playlist):
            self.track_box.selection_set(selected)

    def _create_playlist(self) -> None:
        """Создать новый пустой плейлист."""
        name = simpledialog.askstring("Новый плейлист", "Название:", parent=self)
        if name and name.strip():
            name = name.strip()
            if name in self.playlists:
                messagebox.showerror("Ошибка", "Плейлист с таким именем уже есть.")
            else:
                self.playlists[name] = PlayList()
                self._refresh_playlists(name)

    def _delete_playlist(self) -> None:
        """Удалить выделенный плейлист."""
        selection = self.playlist_box.curselection()
        if selection:
            del self.playlists[self.playlist_box.get(selection[0])]
            self._stop()
            self._refresh_playlists()

    def _add_track(self) -> None:
        """Добавить выбранный аудиофайл в плейлист."""
        playlist = self._selected_playlist()
        if playlist is None:
            return
        path = filedialog.askopenfilename(
            filetypes=[("Аудиофайлы", "*.wav *.mp3 *.ogg"), ("Все файлы", "*.*")]
        )
        if path:
            playlist.append(Composition.from_path(path))
            self._refresh_tracks(len(playlist) - 1)

    def _delete_track(self) -> None:
        """Удалить выделенную композицию."""
        playlist = self._selected_playlist()
        selection = self.track_box.curselection()
        if playlist is not None and selection:
            self._stop()
            playlist.remove(playlist[selection[0]])
            self._refresh_tracks()

    def _move_track(self, direction: int) -> None:
        """Переместить выделенную композицию на одну позицию."""
        playlist = self._selected_playlist()
        selection = self.track_box.curselection()
        if playlist is None or not selection:
            return
        index = selection[0]
        target = index + direction
        if target < 0 or target >= len(playlist):
            return
        self._stop()
        composition = playlist[index].data
        playlist.remove(playlist[index])
        if target == 0:
            playlist.append_left(composition)
        else:
            playlist.insert(playlist[target - 1], composition)
        self._refresh_tracks(target)

    def _start(self, composition: Composition) -> None:
        """Воспроизвести композицию и обновить строку состояния."""
        self._stop()
        try:
            self.audio.play(composition)
            token = self._play_token
            self.status.set(f"Сейчас играет: {composition.title}")
            self.after(100, lambda: self._track_finished(token))
        except (OSError, AudioError) as error:
            messagebox.showerror("Не удалось воспроизвести", str(error))

    def _track_finished(self, token: int) -> None:
        """Запустить следующий трек, только если текущий не был заменён."""
        if token == self._play_token:
            if self.audio.is_playing():
                self.after(100, lambda: self._track_finished(token))
            else:
                self._next()

    def _stop(self) -> None:
        """Остановить музыку и отменить отложенный автопереход."""
        self._play_token += 1
        self.audio.stop()
        self.status.set("Воспроизведение остановлено")

    def _play_selected(self) -> None:
        """Начать воспроизведение с выделенной композиции."""
        playlist = self._selected_playlist()
        selection = self.track_box.curselection()
        if playlist is not None and selection:
            self._start(playlist.play_all(selection[0]))

    def _next(self) -> None:
        """Перейти к следующей композиции."""
        playlist = self._selected_playlist()
        if playlist is not None and len(playlist):
            self._start(playlist.next_track())

    def _previous(self) -> None:
        """Перейти к предыдущей композиции."""
        playlist = self._selected_playlist()
        if playlist is not None and len(playlist):
            self._start(playlist.previous_track())


if __name__ == "__main__":
    PlayerApplication().mainloop()
