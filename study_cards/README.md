# Study Cards

A small Python command-line tool for making and reviewing study cards. It uses
only the Python standard library and stores your deck as a local JSON file.

## Run

From this directory, run:

```bash
python study_cards.py
```

Choose **Add** to create a card, **List** to review the deck, **Delete** to
remove a card, or **Quit** to exit. The default deck file is
`study_cards.json` in the current directory. To use a different file:

```bash
python study_cards.py --data my_deck.json
```

Each change is saved immediately. Keep the JSON file to back up or share your
deck.
