from __future__ import annotations

import argparse
import csv
import os
from typing import List, Dict, Any

from hangman_solver import HangmanSolver


def load_dictionary(path: str) -> List[str]:
    words: List[str] = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            w = line.strip()
            if w:
                words.append(w)
    return words


def solve_file(input_csv: str, output_csv: str, dict_path: str, skip_header: bool, verbose: bool) -> Dict[str, Any]:
    dictionary_words = load_dictionary(dict_path)
    solver = HangmanSolver(dictionary_words)

    os.makedirs(os.path.dirname(output_csv) or ".", exist_ok=True)

    total_valid = 0
    total_invalid = 0
    sum_attempts = 0
    all_ok = True
    invalid_messages: List[str] = []

    results_rows: List[List[str]] = []
    results_rows.append(["game_id", "total_incercari", "cuvant_gasit", "status", "secventa_incercari"])

    with open(input_csv, "r", encoding="utf-8", newline="") as f:
        reader = csv.reader(f)
        if skip_header:
            next(reader, None)

        for idx, row in enumerate(reader, start=1):
            line_no = idx + (1 if skip_header else 0)

            if len(row) < 3:
                total_invalid += 1
                invalid_messages.append(f"Linia {line_no}: prea puține câmpuri (aștept 3).")
                continue

            game_id = str(row[0]).strip()
            pattern_initial = str(row[1]).strip()
            cuvant_tinta = str(row[2]).strip()

            if not game_id or not pattern_initial or not cuvant_tinta:
                total_invalid += 1
                invalid_messages.append(f"Linia {line_no}: câmpuri goale.")
                continue

            if len(pattern_initial) != len(cuvant_tinta):
                total_invalid += 1
                invalid_messages.append(
                    f"Linia {line_no}: lungimi diferite (pattern={len(pattern_initial)} vs cuvant={len(cuvant_tinta)})."
                )
                continue

            total_valid += 1
            res = solver.solve_one(game_id, pattern_initial, cuvant_tinta)
            sum_attempts += res.total_attempts
            if res.status != "OK":
                all_ok = False

            results_rows.append([
                res.game_id,
                str(res.total_attempts),
                res.found_word,
                res.status,
                " ".join(res.attempts_sequence),
            ])

            if verbose:
                print(f"[{res.game_id}] {pattern_initial} -> {res.found_word} ({res.status}) attempts={res.total_attempts}")

    with open(output_csv, "w", encoding="utf-8", newline="") as out:
        writer = csv.writer(out)
        writer.writerows(results_rows)

    return {
        "total_games_valid": total_valid,
        "total_games_invalid": total_invalid,
        "sum_attempts": sum_attempts,
        "all_ok": all_ok,
        "invalid_messages": invalid_messages,
        "output_csv": output_csv,
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True, help="CSV input: game_id,pattern_initial,cuvant_tinta")
    ap.add_argument("--output", required=True, help="CSV output: rezultate")
    ap.add_argument("--dict", required=True, help="Fișier dicționar (1 cuvânt/linie, UTF-8)")
    ap.add_argument("--skip-header", action="store_true", help="Dacă input are header pe prima linie")
    ap.add_argument("--verbose", action="store_true", help="Afișează fiecare joc în consolă")
    args = ap.parse_args()

    summary = solve_file(args.input, args.output, args.dict, args.skip_header, args.verbose)

    print("=== SUMMARY ===")
    print(f"Valid games:   {summary['total_games_valid']}")
    print(f"Invalid lines: {summary['total_games_invalid']}")
    print(f"Sum attempts:  {summary['sum_attempts']}")
    print(f"All OK:        {summary['all_ok']}")
    print(f"Output CSV:    {summary['output_csv']}")
    if summary["invalid_messages"]:
        print("\nInvalid lines details:")
        for m in summary["invalid_messages"]:
            print(" -", m)


if __name__ == "__main__":
    main()
