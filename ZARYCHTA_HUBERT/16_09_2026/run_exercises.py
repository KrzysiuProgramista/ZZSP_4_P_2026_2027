"""Run exercises 2-6. Run test_ex2.py separately for six unit tests."""

import logging

import ex2
import ex3
import ex4
import ex5
import ex6


def main():
    logging.basicConfig(level=logging.WARNING, format="%(levelname)s: %(message)s")
    for exercise in (ex2, ex3, ex4, ex5, ex6):
        exercise.run_demo()


if __name__ == "__main__":
    main()
