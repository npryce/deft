
# Which version of python are we using?
PYTHON=2.7

# Set this on the command-line to select a system-test environment. One of:
#   mem - runs tests using in-memory storage (fast but slight risk of inaccuracy)
#   real - runs tests using disk storage (slow but accurate)
env=real

PYTHON_ENV=python$(PYTHON)-dev

all: test

env:
	virtualenv --python=python$(PYTHON) --no-site-packages $(PYTHON_ENV)
	$(PYTHON_ENV)/bin/pip install argparse
	$(PYTHON_ENV)/bin/pip install pyYAML
	$(PYTHON_ENV)/bin/pip install functional
	$(PYTHON_ENV)/bin/pip install nose
	$(PYTHON_ENV)/bin/pip install PyHamcrest

clean-env:
	rm -rf $(PYTHON_ENV)/

env-again: clean-env env

test: unit-tests system-tests

unit-tests: clean-output-dir
	$(PYTHON_ENV)/bin/nosetests -A "not systest" $(test)

system-tests:
system-tests: clean-output-dir
	DEFT_SYSTEST_ENV=$(env) $(PYTHON_ENV)/bin/nosetests -A "systest" $(test)

wip-tests: clean-output-dir
	$(PYTHON_ENV)/bin/nosetests -A "wip" --no-skip $(test) || true

clean-output-dir:
	rm -rf output/


SCANNED_FILES=src testing-tools deft Makefile

continually:
	@while true; do \
	  clear; \
	  if not make env=$(env); \
	  then \
	      notify-send --icon=error --category=blog --expire-time=1000 "Deft build broken" ; \
	  fi ; \
	  inotifywait -r -qq -e modify -e delete $(SCANNED_FILES); \
	done


.PHONY: all env clean-env env-again test unit-test system-test clean-output-dir continually
