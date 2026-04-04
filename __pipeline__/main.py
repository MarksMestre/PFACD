import subprocess
import sys
import os
import time

# Garante que a raiz está no path para os imports funcionarem
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))

from __pipeline__.generate_files import main as create_files


def main():
    create_files()

    return 0 


if __name__ == "__main__":
    main()