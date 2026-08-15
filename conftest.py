"""Repo-root pytest configuration.

Each generator's ``scripts/`` carries a relative symlink
(``mechanical_checker -> ../../../lib/mechanical-checker``) so its shipped copy
reaches the checker. In this repo those symlinks point back at the one canonical
``lib/mechanical-checker/`` — so a broad ``pytest`` from the repo root would
otherwise descend *through* each symlink and collect the canonical test module
three extra times (once per generator), running every test 4×. That both wastes
work and trips the checker's own duplicate-registration guard.

The canonical copy under ``lib/`` is the one that gets tested here; the symlinked
copies are consumer materialisations, not a second test target. Skip descending
into them. (This file sits at the repo root, above the canonical library dir, so
it is never part of any shipped skill copy.)
"""

collect_ignore_glob = ["skills/*/scripts/mechanical_checker"]
