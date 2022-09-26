# -*- coding: utf-8 -*-
"""
Created on Sat Sep 24 15:44:39 2022

@author: dj079
"""

import logging
import time

logger = logging.getLogger(__name__)

# set format
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# set logging handler and console
handler = logging.FileHandler("log.txt")
handler.setLevel(logging.INFO)

console = logging.StreamHandler()
console.setLevel(logging.INFO)

# Add handlers
logger.addHandler(handler)
logger.addHandler(console)
