"""Repo-root pytest configuration.

This file used to carry ``collect_ignore_glob =
["skills/*/scripts/mechanical_checker"]``. Each generator's ``scripts/`` then
held a relative symlink back at one canonical ``lib/mechanical-checker/``, so a
broad ``pytest`` from the repo root descended *through* every symlink and
collected the canonical test module once per generator — running each test 4×
and tripping the checker's own duplicate-registration guard.

The generator fold left the checker with a single consumer, so it now lives
where it ships — ``skills/build-session/scripts/mechanical_checker/``, a real
directory reached by no symlink at all. There is nothing left to double-collect,
and the glob had to go with the symlinks: keeping it would have silently dropped
the checker's own test modules, which sit at exactly the path it matched.

(This file sits at the repo root, above every shipped skill dir, so it is never
part of a shipped skill copy.)
"""
