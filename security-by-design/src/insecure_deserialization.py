from __future__ import annotations

import argparse
import pickle


def load_untrusted_pickle(path: str):
    with open(path, "rb") as f:
        return pickle.load(f)  # UNSAFE: code execution possible


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--pickle", required=True)
    args = parser.parse_args()
    print("Loading pickle (UNSAFE, demo only)...")
    try:
        obj = load_untrusted_pickle(args.pickle)
        print("Loaded:", obj)
    except Exception as e:
        print("Error (expected in demo without valid pickle):", e)


if __name__ == "__main__":
    main()
