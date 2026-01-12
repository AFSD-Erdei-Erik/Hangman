# Hangman Solver

Solver automat pentru jocul Hangman, care identific? cuvinte pe baza unui pattern par?ial.

## Structura proiectului
- src/ – codul surs?
- data/ – fi?iere CSV ?i dic?ionar
- results/ – rezultate generate
- docs/ – prezentare PPTX

## Rulare
```bash
python src/solve_hangman.py --input data/test.csv --output results/out.csv --dict data/resource.txt --skip-header