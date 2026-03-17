"""Root conftest.py — makes the repo root importable for all tests."""
import sys
import os

# Ensure the repository root is on sys.path so all phase packages are importable
sys.path.insert(0, os.path.dirname(__file__))
