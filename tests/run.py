
import unittest
import argparse
from . import suite


def run() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--level', help='unittest info level, defaults to 2', default=2, type=int)
    args = parser.parse_args()
    runner = unittest.TextTestRunner(verbosity=args.level)
    runner.run(suite())


if __name__ == '__main__':
    run()
