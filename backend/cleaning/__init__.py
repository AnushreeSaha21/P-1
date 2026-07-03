
"""
Cleaning package for FIU Analytics.

This package contains helper functions for:
- Cleaning raw Excel values
- Validating business fields
- Standardizing data before database insertion
"""

from .cleaner import *
from .validators import *
from .standardizer import *





"""
What is __init__.py?

__init__.py tells Python that the cleaning folder is a package. It also lets you import functions cleanly.

Without it:

from backend.cleaning.cleaner import clean_pan

With a well-written __init__.py:

from backend.cleaning import clean_pan

"""