import tempfile
import unittest
from pathlib import Path

from bot import UNKNOWN_ANSWER, find_answer, load_faq, normalize


class FaqBotTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.items = load_faq()

    def test_normalize_removes_punctuation_and_case(self) -> None:
        self.assertEqual(normalize("КаКоЙ ТРЕК?!"), "какой трек")

    def test_finds_answer_by_keyword(self) -> None:
        answer = find_answer("Будут ли призы?", self.items)
        self.assertIn("Нет", answer)

    def test_unknown_question(self) -> None:
        self.assertEqual(find_answer("Какая сегодня погода?", self.items), UNKNOWN_ANSWER)

    def test_faq_contains_five_items(self) -> None:
        self.assertEqual(len(self.items), 5)

    def test_invalid_faq_line_raises_error(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "faq.txt"
            path.write_text("неправильная строка", encoding="utf-8")
            with self.assertRaises(ValueError):
                load_faq(path)


if __name__ == "__main__":
    unittest.main()
