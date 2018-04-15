# -*- coding: utf-8 -*-
from enum import Enum

class State(Enum):
    """
    Состояния бота
    """
    EMAIL = 1
    CHOICE = 2
    QUESTION = 3
    ISSUE = 4
    RESULT = 5