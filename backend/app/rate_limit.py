# -*- coding: utf-8 -*-
"""
Общий rate limiter (slowapi) для защиты от перебора паролей и спама регистраций.
Лимиты считаются по IP клиента. Подключается в main.py (app.state.limiter),
используется декораторами @limiter.limit(...) в роутерах.
"""
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
