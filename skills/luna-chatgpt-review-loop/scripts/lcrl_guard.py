#!/usr/bin/env python3
"""Backward-compatible entry point for V6 callers."""

from lcrl import main


if __name__ == "__main__":
    raise SystemExit(main())
