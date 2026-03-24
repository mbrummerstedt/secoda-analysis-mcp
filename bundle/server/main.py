#!/usr/bin/env python3
"""
Entry point for the Secoda Analysis MCP bundle.

Launches the server via uvx, which downloads and runs
secoda-analysis-mcp from PyPI automatically.
"""
import os
import subprocess
import sys


if __name__ == "__main__":
    result = subprocess.run(["uvx", "secoda-analysis-mcp"], env=os.environ)
    sys.exit(result.returncode)
