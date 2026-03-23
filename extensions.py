"""
Shared Flask extensions — initialised here, attached to the app in create_app().
"""

from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
