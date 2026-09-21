"""Терминальный FAQ-бот для репетиционного трека HackAlem AI."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path


FAQ_FILE = Path(__file__).with_name("faq.txt")
UNKNOWN_ANSWER = "Не знаю"


@dataclass(frozen=True)
class FaqItem:
    question: str
    answer: str
    keywords: tuple[str, ...]


def normalize(text: str) -> str:
    """Приводит текст к нижнему регистру и убирает знаки препинания."""
    return " ".join(re.findall(r"[a-zа-яё0-9]+", text.lower()))


def load_faq(path: Path = FAQ_FILE) -> list[FaqItem]:
    """Загружает FAQ из строк формата: вопрос|ответ|ключевые слова."""
    items: list[FaqItem] = []

    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except FileNotFoundError as error:
        raise RuntimeError(f"Не найден файл FAQ: {path}") from error

    for line_number, raw_line in enumerate(lines, start=1):
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue

        parts = [part.strip() for part in line.split("|")]
        if len(parts) != 3 or not all(parts):
            raise ValueError(
                f"Ошибка в faq.txt, строка {line_number}: "
                "ожидается формат вопрос|ответ|ключевые слова"
            )

        question, answer, raw_keywords = parts
        keywords = tuple(
            normalize(keyword)
            for keyword in raw_keywords.split(",")
            if normalize(keyword)
        )
        items.append(FaqItem(question, answer, keywords))

    if not items:
        raise ValueError("В faq.txt нет ни одной записи")

    return items


def score_question(user_text: str, item: FaqItem) -> int:
    """Считает совпадения слов запроса с вопросом и ключевыми словами."""
    user_words = set(normalize(user_text).split())
    candidate_words = set(normalize(item.question).split())
    for keyword in item.keywords:
        candidate_words.update(keyword.split())
    return len(user_words & candidate_words)


def find_answer(user_text: str, items: list[FaqItem]) -> str:
    """Возвращает ответ на ближайший вопрос или «Не знаю»."""
    best_item: FaqItem | None = None
    best_score = 0

    for item in items:
        score = score_question(user_text, item)
        if score > best_score:
            best_score = score
            best_item = item

    return best_item.answer if best_item is not None else UNKNOWN_ANSWER


def run_chat() -> None:
    """Запускает диалог с пользователем в терминале."""
    items = load_faq()
    print("FAQ-бот HackAlem AI запущен.")
    print("Спросите о времени, команде, треке, сдаче или призах.")
    print("Для выхода напишите: выход")

    while True:
        try:
            user_text = input("\nВы: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nБот: До встречи!")
            break

        if normalize(user_text) in {"выход", "exit", "quit"}:
            print("Бот: До встречи!")
            break
        if not user_text:
            print(f"Бот: {UNKNOWN_ANSWER}")
            continue

        print(f"Бот: {find_answer(user_text, items)}")


if __name__ == "__main__":
    run_chat()
