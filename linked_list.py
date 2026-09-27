"""Кольцевой двусвязный список и модель музыкального плейлиста."""

# Соседние узлы взаимно обновляют внутренние ссылки при связывании.
# pylint: disable=protected-access

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterator, Optional, Union


@dataclass(frozen=True)
class Composition:
    """Музыкальная композиция, доступная для воспроизведения."""

    title: str
    path: str

    @classmethod
    def from_path(cls, path: str) -> "Composition":
        """Создать композицию с названием, взятым из имени файла."""
        return cls(Path(path).stem, path)


class LinkedListItem:
    """Узел кольцевого двусвязного списка."""

    def __init__(self, data: Any = None) -> None:
        """Сохранить данные и создать несвязанный узел."""
        self.data = data
        self._next_item: Optional[LinkedListItem] = None
        self._previous_item: Optional[LinkedListItem] = None

    @property
    def next_item(self) -> Optional["LinkedListItem"]:
        """Вернуть следующий узел."""
        return self._next_item

    @next_item.setter
    def next_item(self, value: Optional["LinkedListItem"]) -> None:
        """Связать узел со следующим и обновить обратную ссылку."""
        self._next_item = value
        if value is not None:
            value._previous_item = self

    @property
    def previous_item(self) -> Optional["LinkedListItem"]:
        """Вернуть предыдущий узел."""
        return self._previous_item

    @previous_item.setter
    def previous_item(self, value: Optional["LinkedListItem"]) -> None:
        """Связать узел с предыдущим и обновить прямую ссылку."""
        self._previous_item = value
        if value is not None:
            value._next_item = self

    def __repr__(self) -> str:
        """Вернуть отладочное представление узла."""
        return f"LinkedListItem({self.data!r})"

    def __eq__(self, other: object) -> bool:
        """Сравнить узел с другим узлом или непосредственно с его данными."""
        if isinstance(other, LinkedListItem):
            return self.data == other.data
        return self.data == other


class LinkedList:
    """Кольцевой двусвязный список узлов :class:`LinkedListItem`."""

    def __init__(self, first_item: Optional[LinkedListItem] = None) -> None:
        """Инициализировать список, возможно уже связанной цепочкой узлов."""
        self.first_item = first_item
        self._length = self._count_items(first_item)
        self._iterator_item: Optional[LinkedListItem] = None
        self._iterator_remaining = 0

    @staticmethod
    def _count_items(first_item: Optional[LinkedListItem]) -> int:
        """Подсчитать узлы, обходя цепочку до начала или её конца."""
        if first_item is None:
            return 0
        count = 1
        current = first_item.next_item
        while current is not None and current is not first_item:
            count += 1
            current = current.next_item
        return count

    @property
    def last(self) -> Optional[LinkedListItem]:
        """Вернуть последний узел или ``None`` для пустого списка."""
        return None if self.first_item is None else self.first_item.previous_item

    def append_left(self, item: Any) -> LinkedListItem:
        """Добавить ``item`` в начало и вернуть созданный узел."""
        node = item if isinstance(item, LinkedListItem) else LinkedListItem(item)
        if self.first_item is None:
            node.next_item = node
            self.first_item = node
        else:
            last = self.last
            assert last is not None
            node.next_item = self.first_item
            last.next_item = node
            self.first_item = node
        self._length += 1
        return node

    def append_right(self, item: Any) -> LinkedListItem:
        """Добавить ``item`` в конец и вернуть созданный узел."""
        if self.first_item is None:
            return self.append_left(item)
        node = item if isinstance(item, LinkedListItem) else LinkedListItem(item)
        last = self.last
        assert last is not None
        last.next_item = node
        node.next_item = self.first_item
        self._length += 1
        return node

    def append(self, item: Any) -> LinkedListItem:
        """Добавить ``item`` в конец списка."""
        return self.append_right(item)

    def _find_node(self, item: Any) -> Optional[LinkedListItem]:
        """Найти первый узел с данными ``item`` или сам переданный узел."""
        for node in self:
            if node is item or node.data == item:
                return node
        return None

    def remove(self, item: Any) -> None:
        """Удалить первый узел с ``item``; при отсутствии возбудить ValueError."""
        node = self._find_node(item)
        if node is None:
            raise ValueError(f"Элемент {item!r} отсутствует в списке")
        if self._length == 1:
            self.first_item = None
        else:
            previous = node.previous_item
            following = node.next_item
            assert previous is not None and following is not None
            previous.next_item = following
            if node is self.first_item:
                self.first_item = following
        node._next_item = None
        node._previous_item = None
        self._length -= 1

    def insert(self, previous: Any, item: Any) -> LinkedListItem:
        """Вставить ``item`` после узла или данных ``previous``."""
        previous_node = self._find_node(previous)
        if previous_node is None:
            raise ValueError(f"Элемент {previous!r} отсутствует в списке")
        node = item if isinstance(item, LinkedListItem) else LinkedListItem(item)
        following = previous_node.next_item
        previous_node.next_item = node
        node.next_item = following
        self._length += 1
        return node

    def __len__(self) -> int:
        """Вернуть количество узлов."""
        return self._length

    def __iter__(self) -> "LinkedList":
        """Подготовить обход от первого до последнего узла."""
        self._iterator_item = self.first_item
        self._iterator_remaining = self._length
        return self

    def __next__(self) -> LinkedListItem:
        """Вернуть очередной узел при прямом обходе."""
        if self._iterator_remaining == 0 or self._iterator_item is None:
            raise StopIteration
        node = self._iterator_item
        self._iterator_item = node.next_item
        self._iterator_remaining -= 1
        return node

    def __getitem__(self, index: int) -> LinkedListItem:
        """Вернуть узел по положительному или отрицательному индексу."""
        if not isinstance(index, int):
            raise TypeError("Индекс должен быть целым числом")
        if index < 0:
            index += self._length
        if index < 0 or index >= self._length:
            raise IndexError("Индекс вне диапазона списка")
        current = self.first_item
        for _ in range(index):
            assert current is not None
            current = current.next_item
        assert current is not None
        return current

    def __contains__(self, item: Any) -> bool:
        """Проверить наличие данных или узла в списке."""
        return self._find_node(item) is not None

    def __reversed__(self) -> Iterator[LinkedListItem]:
        """Обойти список от последнего узла к первому."""
        current = self.last
        for _ in range(self._length):
            assert current is not None
            yield current
            current = current.previous_item


class PlayList(LinkedList):
    """Плейлист, хранящий композиции и текущую позицию воспроизведения."""

    def __init__(self, first_item: Optional[LinkedListItem] = None) -> None:
        """Создать плейлист без выбранной композиции."""
        super().__init__(first_item)
        self._current_item: Optional[LinkedListItem] = None

    @property
    def current(self) -> Optional[Composition]:
        """Вернуть текущую композицию или ``None``."""
        if self._current_item is None:
            return None
        return self._current_item.data

    def play_all(self, item: Union[LinkedListItem, Composition, int]) -> Composition:
        """Начать воспроизведение с переданного узла, композиции или индекса."""
        if isinstance(item, int):
            node = self[item]
        else:
            node = self._find_node(item)
        if node is None:
            raise ValueError("Композиция отсутствует в плейлисте")
        self._current_item = node
        return node.data

    def next_track(self) -> Composition:
        """Перейти к следующей композиции, возвращаясь к началу плейлиста."""
        if self._current_item is None:
            if self.first_item is None:
                raise ValueError("Плейлист пуст")
            self._current_item = self.first_item
        else:
            self._current_item = self._current_item.next_item
        assert self._current_item is not None
        return self._current_item.data

    def previous_track(self) -> Composition:
        """Перейти к предыдущей композиции."""
        if self._current_item is None:
            if self.last is None:
                raise ValueError("Плейлист пуст")
            self._current_item = self.last
        else:
            self._current_item = self._current_item.previous_item
        assert self._current_item is not None
        return self._current_item.data

    def remove(self, item: Any) -> None:
        """Удалить композицию и сбросить текущую позицию при необходимости."""
        node = self._find_node(item)
        if node is self._current_item:
            self._current_item = node.next_item if len(self) > 1 else None
        super().remove(item)
