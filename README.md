# Checkers Game

A small command-line checkers game in Python.

## Project structure

- `src/` — game implementation and CLI entrypoint
- `tests/` — unit tests for move validation and game rules
- `examples/` — usage examples and commands

## Run locally

From the repository root:

```powershell
python src\main.py
```

Then enter moves like `b6-a5` or `b6xc4`.

## Run tests

Install `pytest` if needed:

```powershell
pip install pytest
```

Run tests from the repository root:

```powershell
pytest
```

## Notes

- Only dark squares are playable.
- Capture moves are mandatory.
- Pieces are promoted to kings at the opposite side.

## About this repo

This repository is a minimal reproducible checkers project with a CLI, unit tests, and example usage.
