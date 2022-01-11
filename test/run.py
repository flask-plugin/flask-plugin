
import argparse
from . import _run_tests

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--level', help='unittest info level, defaults to 2', default=2, type=int)
    args = parser.parse_args()
    _run_tests(args.level)
