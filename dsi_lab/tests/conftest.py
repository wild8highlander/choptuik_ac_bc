# -*- coding: utf-8 -*-
"""conftest: делаем корень dsi_lab импортируемым при любом способе запуска."""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
