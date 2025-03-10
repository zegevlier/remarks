# Testing remarks

Testing is still a work-in-progress, but is integral to good software.

## Set-up

Simply run the nix development environment, as usual:

```shell
$ nix-shell
```

## Running tests

Run tests with `pytest`. Tests are also automatically ran prior to committing.

```shell
$ pytest
# or run the tests in watch mode, during development
$ bash testloop
```

## Directory structure

We have a "tests" directory where test data is stored. Each folder represents an exported ReMarkable notebook file.

- `tests/in` stores ReMarkable notebook files. Each directory represents one notebook
- `tests/out` is a directory which stores the PDF and markdown files generated by remarks.
  This directory can be cleared whenever you wish.
