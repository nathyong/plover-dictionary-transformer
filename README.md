# Plover dictionary transformer

Dictionaries not included.  Consider this repository unmaintained.

- `stroke.py`: utilities for representing a Plover stroke, and decomposing it
- `ipa.py`: utilities for transforming IPA in text format
- `transform.py`: transforms a dictionary with various rules.

A few rules are included for Phoenix and Plover theories.

## Toolchain

- Python 3.6+
- Static type checking with `mypy --check-untyped-defs`
- Tests with `pytest --doctest-modules`
- espeak

If you have Nix, you can use the nix-shell to get these dependencies quickly.
