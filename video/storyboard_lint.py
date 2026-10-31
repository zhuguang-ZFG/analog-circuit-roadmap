#!/usr/bin/env python3
"""Offline structural preflight shared by director and the Remotion registry.

validate_storyboard(board, *, svg_dir, custom_views=()) returns list[str]:
[] means valid; errors use zero-based shots[i].field paths. It never mutates
boards and does not impose editorial limits on text, pacing or total duration.
load_storyboard adds file/JSON diagnostics and raises ValidationError on failure.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
import re
import sys

VIDEO_DIR = Path(__file__).resolve().parent
SVG_DIR = VIDEO_DIR.parent / "assets" / "svg"
FPS = 30
TRANSITION_FRAMES = 9

# Single source for episode registration AND validation. Values are TS component
# names; gen_registry derives both imports and customShots from this structure.
CUSTOM_VIEWS: dict[str, dict[str, str]] = {
    "ep04": {"demo": "DividerDemo", "collapse": "DividerCollapse"},
}
BUILTIN_VIEWS = {"quiz", "noise-rss"}
SHOT_TYPES = {"intro", "card", "num", "svg"}
_SAFE_STEM = re.compile(r"[A-Za-z0-9][A-Za-z0-9_-]*")
_RESERVED_STEMS = {"CON", "PRN", "AUX", "NUL", "CONIN$", "CONOUT$"} | {
    f"{prefix}{n}" for prefix in ("COM", "LPT") for n in range(1, 10)
}
_TEXT_FIELDS = ("eyebrow", "sub", "chip", "mascot", "bubble", "cta", "caption",
                "series", "ep", "progress", "explain")


def custom_views_for_name(name: object) -> dict[str, str]:
    """Resolve source/draft board names, e.g. ep04-divider -> ep04.

    Registry callers must instead use the actual registration key (file stem),
    so a board named ep04-divider cannot enable demo in an ep20 registration.
    """
    if not isinstance(name, str):
        return {}
    return CUSTOM_VIEWS.get(name.split("-", 1)[0], {})


def _safe_stem(value: object) -> bool:
    return (isinstance(value, str) and _SAFE_STEM.fullmatch(value) is not None
            and value.upper() not in _RESERVED_STEMS)


def _finite(value: object) -> bool:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return False
    try:
        return math.isfinite(value)
    except OverflowError:
        return False


def _strings(value: object) -> bool:
    return isinstance(value, list) and all(isinstance(item, str) for item in value)


def validate_storyboard(board: object, *, svg_dir: str | Path,
                        custom_views=()) -> list[str]:
    """Check the shared rendering contract; custom_views is an iterable of keys.

    Built-in views require type=card but may omit lines (legacy draft is empty).
    Other types retain their base fields for director's generic draft fallback.
    Frame checks mirror Episode's cumulative Math.round(t * 30) boundaries.
    """
    errors: list[str] = []
    if not isinstance(board, dict):
        return ["$: expected a storyboard object"]
    if not _safe_stem(board.get("name")):
        errors.append("name: expected a safe filename stem (letters, digits, _ or -; no paths)")
    shots = board.get("shots")
    if not isinstance(shots, list) or not shots:
        return errors + ["shots: expected a non-empty array"]

    allowed_views = BUILTIN_VIEWS | set(custom_views)
    svg_dir = Path(svg_dir)
    accumulated = 0.0
    previous_bound = 0
    for i, shot in enumerate(shots):
        prefix = f"shots[{i}]"
        if not isinstance(shot, dict):
            errors.append(f"{prefix}: expected a shot object")
            continue

        def error(field: str, message: str) -> None:
            errors.append(f"{prefix}.{field}: {message}")

        def asset(field: str) -> None:
            stem = shot.get(field)
            if not _safe_stem(stem):
                error(field, "expected a safe SVG stem without path or .svg extension")
            elif not (svg_dir / f"{stem}.svg").is_file():
                error(field, f"missing SVG asset: {svg_dir / (stem + '.svg')}")

        kind = shot.get("type")
        if not isinstance(kind, str) or kind not in SHOT_TYPES:
            error("type", "expected intro, card, num or svg")
        view = shot.get("view")
        has_view = "view" in shot
        valid_view = isinstance(view, str) and view in allowed_views
        if has_view and not valid_view:
            error("view", "unknown view for this episode registration")
        if isinstance(view, str) and view in BUILTIN_VIEWS and kind != "card":
            error("type", f"built-in view {view!r} requires card")

        seconds = shot.get("seconds")
        frames = None
        if not _finite(seconds) or seconds <= 0:
            error("seconds", "expected a finite positive number (not a boolean)")
        elif not _finite((accumulated + seconds) * FPS):
            error("seconds", "30fps frame boundary must be finite")
        else:
            accumulated += seconds
            bound = math.floor(accumulated * FPS + 0.5)  # JS Math.round, not banker's round
            frames = bound - previous_bound
            previous_bound = bound
            if math.floor(seconds * FPS + 0.5) < 1 or frames < 1:
                error("seconds", "duration rounds to zero frames at 30fps (including cumulative bounds)")
            # Episode pads every non-final sequence with T frames, so only the
            # final shot of a multi-shot board can be shorter than its transition.
            elif len(shots) > 1 and i == len(shots) - 1 and frames < TRANSITION_FRAMES:
                error("seconds", "final shot needs at least 9 cumulative frames for the incoming transition")
            # Remotion interpolate inputRange must be strictly increasing.
            # A valid view bypasses these generic components entirely.
            if not valid_view and kind == "card" and frames <= 18:
                error("seconds", "CardShot needs >18 cumulative frames for interpolate([18, durFrames])")
            if not valid_view and kind == "svg" and frames <= 27:
                error("seconds", "SvgShot needs >27 cumulative frames for interpolate([27, durFrames])")

        for field in _TEXT_FIELDS:
            if field in shot and not isinstance(shot[field], str):
                error(field, "expected a string when present")
        if "lines" in shot or (kind == "card" and not has_view):
            if not _strings(shot.get("lines")):
                error("lines", "expected an array of strings (may be empty)")
        if kind == "intro":
            title = shot.get("title")
            if not isinstance(title, str) or not title.strip():
                error("title", "expected a non-empty string")
        elif kind == "num":
            for field in ("from", "to"):
                if not _finite(shot.get(field)):
                    error(field, "expected a finite number (not a boolean)")
            unit = shot.get("unit")
            if not isinstance(unit, str) or not unit.strip():
                error("unit", "expected a non-empty string")
            dec = shot.get("dec", 1)
            if type(dec) is not int or not 0 <= dec <= 100:
                error("dec", "expected an integer from 0 to 100 (JavaScript toFixed range)")
            bar = shot.get("bar")
            if bar is not None and (not isinstance(bar, list) or len(bar) != 2
                                    or not all(_finite(value) for value in bar)):
                error("bar", "expected two finite numbers")
        elif kind == "svg":
            asset("file")
        if "bgSvg" in shot:
            asset("bgSvg")
        if view == "quiz":
            if "revealAt" in shot:
                reveal_at = shot["revealAt"]
                if not _finite(reveal_at) or reveal_at < 0:
                    error("revealAt", "expected a finite non-negative number (not a boolean)")
                elif _finite(seconds) and reveal_at >= seconds:
                    error("revealAt", "must be less than seconds")
                elif frames is not None and math.floor(reveal_at * FPS + 0.5) >= frames:
                    error("revealAt", "must leave at least one actual scene frame after 30fps rounding")
            if not isinstance(shot.get("q"), str):
                error("q", "quiz requires a string question")
            options = shot.get("options", [])
            if not _strings(options) or len(options) > 3:
                error("options", "expected an array of at most 3 strings; omit or use [] for thinking mode")
            elif options:
                answer = shot.get("answer")
                if type(answer) is not int or not 0 <= answer < len(options):
                    error("answer", "expected a 0-based integer index within options")
    return errors


class ValidationError(ValueError):
    """A file could not be loaded or did not pass preflight."""


def load_storyboard(path: str | Path, *, svg_dir: str | Path = SVG_DIR,
                    custom_views=None) -> dict:
    """Read and validate a file; explicit custom_views overrides name inference."""
    path = Path(path).resolve()
    try:
        board = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, ValueError) as exc:
        raise ValidationError(f"{path}: $: cannot read storyboard JSON: {exc}") from None
    if custom_views is None:
        custom_views = custom_views_for_name(board.get("name") if isinstance(board, dict) else None)
    errors = validate_storyboard(board, svg_dir=svg_dir, custom_views=custom_views)
    if errors:
        raise ValidationError("\n".join(f"{path}: {error}" for error in errors))
    return board


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Offline storyboard preflight (shot indices are zero-based)")
    parser.add_argument("paths", nargs="*", type=Path,
                        help="JSON paths; defaults to video/shots/ep*.json")
    args = parser.parse_args(argv)
    paths = args.paths or sorted((VIDEO_DIR / "shots").glob("ep*.json"))
    if not paths:
        print(f"{VIDEO_DIR / 'shots'}: $: no ep*.json storyboards found", file=sys.stderr)
        return 1
    failed = 0
    for path in paths:
        try:
            load_storyboard(path)
        except ValidationError as exc:
            print(exc, file=sys.stderr)
            failed += 1
        else:
            print(f"{path.resolve()}: OK")
    print(f"Preflight: {len(paths)} files, {failed} failed")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
