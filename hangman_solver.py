from __future__ import annotations

from dataclasses import dataclass
from typing import List, Dict, Set, Tuple, Optional
from collections import Counter
import re


def normalize_word(s: str) -> str:
    """
    Normalizează: lower + strip.
    Păstrează diacriticele (ăâîșț) ca litere distincte.
    """
    return s.strip().lower()


def pattern_to_regex(pattern: str) -> re.Pattern:
    """
    Transformă pattern cu '*' în regex.
    Ex: st****t -> ^st....t$
    """
    escaped = []
    for ch in pattern:
        if ch == "*":
            escaped.append(".")
        else:
            escaped.append(re.escape(ch))
    return re.compile("^" + "".join(escaped) + "$")


def apply_guess_to_pattern(pattern: str, candidate: str, guess: str) -> str:
    """
    Actualizează pattern-ul cu litera guess, pe baza unui cuvânt candidat.
    """
    out = list(pattern)
    for i, c in enumerate(candidate):
        if c == guess:
            out[i] = guess
    return "".join(out)


@dataclass
class SolveResult:
    game_id: str
    total_attempts: int
    found_word: str
    status: str
    attempts_sequence: List[str]


class HangmanSolver:
    """
    Solver Hangman bazat pe dicționar offline.
    Strategia:
      1) Filtrăm candidații după pattern.
      2) Alegem litera cu frecvența maximă în candidați (doar în pozițiile necunoscute).
      3) Actualizăm pattern-ul și repetăm până rămâne un singur cuvânt.
    """

    def __init__(self, dictionary_words: List[str]):
        self.dictionary = [normalize_word(w) for w in dictionary_words if normalize_word(w)]

    def solve_one(self, game_id: str, pattern_initial: str, target_word: str) -> SolveResult:
        pattern = normalize_word(pattern_initial)
        target = normalize_word(target_word)

        attempts: List[str] = []
        guessed: Set[str] = set()

        # inițial: candidați după lungime + regex pattern
        rx = pattern_to_regex(pattern)
        candidates = [w for w in self.dictionary if len(w) == len(pattern) and rx.match(w)]

        # Dacă dicționarul nu conține cuvântul, tot încercăm cu candidați (poate nu e în dict)
        # Dar pentru proiect, dict ar trebui să conțină.
        while True:
            # dacă pattern nu mai are '*', putem decide direct
            if "*" not in pattern:
                found = pattern
                break

            if len(candidates) <= 1:
                found = candidates[0] if candidates else pattern.replace("*", "")
                break

            # alegem litera optimă (frecvență mare în candidați, doar în pozițiile '*')
            unknown_positions = [i for i, ch in enumerate(pattern) if ch == "*"]
            freq = Counter()
            for w in candidates:
                for i in unknown_positions:
                    ch = w[i]
                    if ch not in guessed:
                        freq[ch] += 1

            if not freq:
                # fallback: ia prima literă neghicită din candidați
                for w in candidates:
                    for ch in w:
                        if ch not in guessed:
                            freq[ch] = 1
                            break
                    if freq:
                        break

            guess = freq.most_common(1)[0][0]
            guessed.add(guess)
            attempts.append(guess)

            # simulăm ghicirea vs target (target e doar pt evaluare)
            if guess in target:
                pattern = apply_guess_to_pattern(pattern, target, guess)

            # refacem candidații după noul pattern
            rx = pattern_to_regex(pattern)
            candidates = [w for w in candidates if rx.match(w)]

        status = "OK" if found == target else "FAIL"
        return SolveResult(
            game_id=game_id,
            total_attempts=len(attempts),
            found_word=found,
            status=status,
            attempts_sequence=attempts,
        )
