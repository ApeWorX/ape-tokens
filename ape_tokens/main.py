"""
Separated from __init__.py so CLI module loads faster during --help.
"""

from .managers import TokenManager as _TokenManager

tokens = _TokenManager()
