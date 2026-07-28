<<<<<<< HEAD
# Advanced Scientific Calculator

A modern, Windows 11-style scientific calculator built with Python and CustomTkinter.

## Features
The app has 5 tabs:

1. **Calculator** — basic + scientific operations (sin, cos, tan, inverse trig, log, ln, sqrt, powers, factorial), constants `pi`/`e`, memory buttons (MC/MR/M+/M-), persistent history panel (click an entry to reuse it), keyboard shortcuts (digits, `+ - * / ( )`, `Enter` to calculate, `Backspace` to delete, `Esc` to clear)
2. **Graphing** — plot any function of `x` (e.g. `sin(x)`, `x**2 - 3*x + 1`) over a custom x-range
3. **Converter** — Length, Weight, Volume, Speed, and Temperature unit conversion with a swap button
4. **Programmer** — live Binary/Octal/Decimal/Hexadecimal conversion, plus bitwise & arithmetic operations (AND, OR, XOR, NOT, shifts, +, -, *, /)
5. **Percentage & Tip** — quick "X% of Y" calculator, plus a full tip calculator (bill split across people, quick 10/15/18/20/25% buttons)

Dark / Light / **Cartoon** theme (click the theme button top-right to cycle through all three) applies across all tabs. Cartoon mode adds a playful comic-style look (bold candy colors, thick borders, Comic Sans font) plus fun effects: the result **pops** with a bounce and a **confetti burst** plays every time you hit `=` successfully. Safe expression evaluation is used throughout (no raw `eval()` on user input).

## Project structure
```
Advanced-Scientific-Calculator/
│
├── main.py          # entry point
├── ui.py            # CustomTkinter UI (all 5 tabs)
├── calculator.py     # math engine (safe parser/evaluator, supports variables for graphing)
├── converter.py       # unit conversion logic
├── baseconv.py        # number base conversion + bitwise ops
├── history.py        # history load/save/clear
├── theme.py          # dark/light color palettes
├── requirements.txt
├── README.md
└── data/              # created automatically, stores history.json
```

## Setup

1. Make sure you have Python 3.9+ installed.
2. Open this folder in VS Code / terminal.
3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
4. Run the app:
   ```
   python main.py
   ```

## Notes
- The `data/` folder and `history.json` are created automatically on first run — you don't need to create them manually.
- If you ever see `ModuleNotFoundError`, it almost always means a `.py` file is missing or misnamed in this folder — run `dir` (Windows) or `ls` (Mac/Linux) to confirm all 5 `.py` files listed above are present.

## Building a Windows .exe (optional, next step)
Once you confirm the app runs correctly with `python main.py`, you can package it as a standalone `.exe`:
```
pip install pyinstaller
pyinstaller --onefile --windowed --name "ScientificCalculator" main.py
```
The executable will appear in the `dist/` folder.
=======
# Advanced-Scientific-Calculator
Here's a version of about **250 characters** (roughly 100 more than the previous one):  **Advanced Scientific Calculator:** A modern desktop calculator built with Python and CustomTkinter, featuring basic and advanced scientific operations, calculation history, memory functions, theme customization, keyboard shortcuts, and a clean, user-friend
>>>>>>> a11de6ad41381525ca1e72422e14802902e6695a
