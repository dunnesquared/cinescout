"""Ensures Python can find cinescout modules and object for test files.
Source: https://docs.python-guide.org/writing/structure/
"""
import os
import sys


print("Running unit tests...")
print("Building path that will allow python to find to app resources...")

new_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, new_path)

print(f"New path inserted into sys.path:\n{new_path}")

from cinescout import app, db
from config import basedir
from cinescout.models import User
