from __future__ import annotations
import logging
import sys
from pathlib import Path
from typing import List
from abc import abstractmethod, ABC
from types import SimpleNamespace
import os
from main import main as _root

if __name__ == '__main__':
    _root = _root()
    _root.info(f'||{__file__}_root()||')
    _runtime = logging.getLogger('runtime')
    _runtime.info(f'||{__file__}_runtime()||')
else:
    _runtime = logging.getLogger('runtime')
    _runtime.info(f'||{__file__}_runtime()||')
