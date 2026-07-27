"""
theme.py
Color palettes for the calculator's Dark, Light, and Cartoon modes.
"""

THEMES = {
    "Dark": {
        "bg": "#1e1e1e",
        "display_bg": "#2b2b2b",
        "display_fg": "#ffffff",
        "btn_bg": "#2f2f2f",
        "btn_fg": "#ffffff",
        "btn_hover": "#3f3f3f",
        "op_btn_bg": "#3a3a3a",
        "op_btn_hover": "#4a4a4a",
        "accent_bg": "#0a84ff",
        "accent_hover": "#3a9bff",
        "history_bg": "#232323",
        "history_fg": "#dddddd",
        "font_family": "Segoe UI",
        "corner_radius": 10,
        "border_width": 0,
        "border_color": "#2f2f2f",
        "confetti_colors": ["#0a84ff", "#ffffff", "#3a9bff"],
    },
    "Light": {
        "bg": "#f2f2f2",
        "display_bg": "#ffffff",
        "display_fg": "#1a1a1a",
        "btn_bg": "#e6e6e6",
        "btn_fg": "#1a1a1a",
        "btn_hover": "#d6d6d6",
        "op_btn_bg": "#dedede",
        "op_btn_hover": "#cfcfcf",
        "accent_bg": "#0a84ff",
        "accent_hover": "#3a9bff",
        "history_bg": "#ffffff",
        "history_fg": "#1a1a1a",
        "font_family": "Segoe UI",
        "corner_radius": 10,
        "border_width": 0,
        "border_color": "#dedede",
        "confetti_colors": ["#0a84ff", "#3a9bff", "#1a1a1a"],
    },
    "Cartoon": {
        "bg": "#fff3d6",
        "display_bg": "#ffffff",
        "display_fg": "#2b2b2b",
        "btn_bg": "#ffd93d",
        "btn_fg": "#2b2b2b",
        "btn_hover": "#ffc300",
        "op_btn_bg": "#4ea8de",
        "op_btn_hover": "#3d8bc4",
        "accent_bg": "#ff6b6b",
        "accent_hover": "#ff4757",
        "history_bg": "#ffffff",
        "history_fg": "#2b2b2b",
        "font_family": "Comic Sans MS",
        "corner_radius": 22,
        "border_width": 3,
        "border_color": "#2b2b2b",
        "confetti_colors": ["#ff6b6b", "#ffd93d", "#4ea8de", "#51cf66", "#cc5de8"],
    },
}


def get_theme(mode: str) -> dict:
    """Return the color dictionary for the requested mode."""
    return THEMES.get(mode, THEMES["Dark"])
