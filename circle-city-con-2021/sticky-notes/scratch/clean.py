#!/usr/bin/env python3
# Example script to test behavior of path cleaning in note server
import re
import sys
from pathlib import Path

route = sys.argv[1]
print(f"Before: {route}")
filepath_re = re.compile(r"[^a-z0-9-/]")

route = filepath_re.sub("", route).strip("/")
print(f"After: {route}")

filepath = Path("/tmp/boards") / route
print(f"Path: {filepath}")
