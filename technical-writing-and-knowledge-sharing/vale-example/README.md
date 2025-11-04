# Vale example

A minimal, self-contained Vale setup for linting Markdown prose. It defines two custom rules (weasel words and passive voice) and includes a sample file to lint.

## What’s included

- `.vale.ini` — Configuration pointing to `Styles/` and enabling our custom style for `*.md`.
- `Styles/HouseStyle/WeaselWords.yml` — Flags vague/weasel words like “very”, “really”, “just”, etc.
- `Styles/HouseStyle/PassiveVoice.yml` — Heuristic check for passive voice (e.g., “was implemented”).
- `docs/sample.md` — A sample with deliberate issues to exercise the rules.

## How to run (Linux)

1. Install Vale

- Option A (Homebrew):

```bash
brew install vale
```

- Option B (Download binary): See the official releases: [github.com/errata-ai/vale/releases](https://github.com/errata-ai/vale/releases)

1. Run Vale against the sample

```bash
cd technical-writing-and-knowledge-sharing/vale-example
vale docs/sample.md
```

1. Run Vale against all Markdown files in this folder

```bash
vale .
```

## VS Code integration (optional)

- Install the “Vale” extension (errata-ai.vale-server).
- Open this folder; the extension will pick up `.vale.ini` and annotate issues inline.

## Notes

- The passive voice rule is intentionally simple; it may produce false positives/negatives. For production use, prefer a maintained style (e.g., write-good) or refine the regex/rules.
- You can add more rules under `Styles/HouseStyle/` and list them in `.vale.ini` via `BasedOnStyles = HouseStyle` (already set for `*.md`).
