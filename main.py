#!/bin/python3
# coding=utf-8

import logging
import os

logging.basicConfig(
    format=os.getenv(
        "LOGFORMAT", "[%(levelname)s] [%(filename)s:%(lineno)d] %(message)s"
    ),
    level=os.getenv("LOGLEVEL", "WARNING"),
    force=True,
)

from banking.api import app as bankingapi

if __name__ == "__main__":
    bankingapi.run(debug=True)
