"""Автоматические тесты структур данных плеера."""

import unittest

from linked_list import Composition, LinkedList, PlayList


class LinkedListTests(unittest.TestCase):
    """Проверки кольцевого двусвязного списка."""

    def test_append_and_iteration(self) -> None:
        """Добавленные элементы сохраняют порядок и кольцевые ссылки."""
        linked_list = LinkedList()
        linked_list.append("второй")
        linked_list.append_left("первый")
        linked_list.append("третий")
        self.assertEqual([node.data for node in linked_list], ["первый", "второй", "третий"])
        self.assertIs(linked_list.last.next_item, linked_list.first_item)
        self.assertIs(linked_list.first_item.previous_item, linked_list.last)

    def test_indexing_removal_and_insert(self) -> None:
        """Индексы, вставка и удаление изменяют список корректно."""
        linked_list = LinkedList()
        for item in (1, 2, 3):
            linked_list.append(item)
        linked_list.insert(linked_list[0], 10)
        linked_list.remove(2)
        self.assertEqual([node.data for node in linked_list], [1, 10, 3])
        self.assertEqual(linked_list[-1].data, 3)
        self.assertEqual([node.data for node in reversed(linked_list)], [3, 10, 1])

    def test_removing_missing_item_fails(self) -> None:
        """Отсутствующий элемент вызывает требуемое исключение."""
        with self.assertRaises(ValueError):
            LinkedList().remove("нет")


class PlayListTests(unittest.TestCase):
    """Проверки навигации плейлиста."""

    def test_next_track_loops_to_start(self) -> None:
        """После последней композиции воспроизводится первая."""
        playlist = PlayList()
        first = Composition("Первая", "first.wav")
        second = Composition("Вторая", "second.wav")
        playlist.append(first)
        playlist.append(second)
        self.assertEqual(playlist.play_all(0), first)
        self.assertEqual(playlist.next_track(), second)
        self.assertEqual(playlist.next_track(), first)
        self.assertEqual(playlist.previous_track(), second)


if __name__ == "__main__":
    unittest.main()
