"""
Author: Martin

Date: 2025-09-24

License: Unlicense

Description:
    Logging setup
"""

import logging

logger = logging.getLogger("detritus")
logger.setLevel(logging.DEBUG)

console = logging.StreamHandler()
formatter = logging.Formatter("[%(asctime)s] [%(levelname)s] %(message)s")
console.setFormatter(formatter)

logger.addHandler(console)
