"""Create and manage a small, local study-card deck."""

from __future__ import annotations

import argparse
import json
import random
from dataclasses import asdict, dataclass
from pathlib import Path


@dataclass
class Card:
    term: str
    definition: str


class CardStore:
    """Load and save cards in a simple JSON file."""

    def __init__(self, path: Path) -> None:
        self.path = path

    def load(self) -> list[Card]:
        if not self.path.exists():
            return []

        try:
            raw_cards = json.loads(self.path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as error:
            raise ValueError(f"{self.path} is not valid JSON.") from error

        if not isinstance(raw_cards, list):
            raise ValueError(f"{self.path} must contain a JSON list of cards.")

        cards: list[Card] = []
        for number, item in enumerate(raw_cards, start=1):
            if (
                not isinstance(item, dict)
                or not isinstance(item.get("term"), str)
                or not isinstance(item.get("definition"), str)
            ):
                raise ValueError(f"Card {number} in {self.path} is missing text fields.")
            cards.append(Card(item["term"], item["definition"]))
        return cards

    def save(self, cards: list[Card]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        temporary_path = self.path.with_suffix(self.path.suffix + ".tmp")
        payload = [asdict(card) for card in cards]
        temporary_path.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        temporary_path.replace(self.path)


def add_card(cards: list[Card], store: CardStore) -> None:
    term = input("Term or question: ").strip()
    definition = input("Definition or answer: ").strip()
    if not term or not definition:
        print("Both sides need text; no card was added.")
        return

    cards.append(Card(term, definition))
    store.save(cards)
    print("Card saved.")


def list_cards(cards: list[Card]) -> None:
    if not cards:
        print("Your deck is empty. Add a card to get started.")
        return

    for number, card in enumerate(cards, start=1):
        print(f"{number}. {card.term} — {card.definition}")


def delete_card(cards: list[Card], store: CardStore) -> None:
    if not cards:
        print("Your deck is empty.")
        return

    list_cards(cards)
    choice = input("Card number to delete (or Enter to cancel): ").strip()
    if not choice:
        print("Delete cancelled.")
        return

    try:
        index = int(choice) - 1
    except ValueError:
        print("Enter a card number from the list.")
        return

    if index < 0 or index >= len(cards):
        print("That card number is not in the list.")
        return

    removed = cards.pop(index)
    store.save(cards)
    print(f"Deleted “{removed.term}”.")


def study_deck(cards: list[Card]) -> None:
    if not cards:
        print("Your deck is empty. Add a card before starting a study session.")
        return

    session = cards.copy()
    random.shuffle(session)
    known = 0
    review: list[Card] = []
    studied = 0

    print("\nStudy session — try to recall each answer before revealing it.")
    for number, card in enumerate(session, start=1):
        print(f"\nCard {number} of {len(session)}: {card.term}")
        action = input("Press Enter to reveal, or Q to stop: ").strip().lower()
        if action in {"q", "quit"}:
            break

        print(f"Answer: {card.definition}")
        while True:
            rating = input("[K]new it or [R]eview again? ").strip().lower()
            if rating in {"k", "knew", "r", "review"}:
                break
            print("Choose K if you knew it, or R to review it again.")

        studied += 1
        if rating in {"k", "knew"}:
            known += 1
        else:
            review.append(card)

    print(f"\nSession complete: {known} knew, {len(review)} to review, {studied} studied.")
    if review:
        print("Review these cards:")
        for card in review:
            print(f"- {card.term} — {card.definition}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Make a local study-card deck.")
    parser.add_argument(
        "--data",
        type=Path,
        default=Path("study_cards.json"),
        help="deck file to use (default: study_cards.json)",
    )
    args = parser.parse_args()
    store = CardStore(args.data)

    try:
        cards = store.load()
    except (OSError, ValueError) as error:
        print(f"Could not load deck: {error}")
        return 1

    while True:
        print("\nStudy Cards")
        print("[A]dd  [L]ist  [D]elete  [S]tudy  [Q]uit")
        choice = input("> ").strip().lower()

        try:
            if choice in {"a", "add"}:
                add_card(cards, store)
            elif choice in {"l", "list"}:
                list_cards(cards)
            elif choice in {"d", "delete"}:
                delete_card(cards, store)
            elif choice in {"s", "study"}:
                study_deck(cards)
            elif choice in {"q", "quit"}:
                print("Deck saved. Happy studying!")
                return 0
            else:
                print("Choose Add, List, Delete, Study, or Quit.")
        except OSError as error:
            print(f"Could not save deck: {error}")


if __name__ == "__main__":
    raise SystemExit(main())
