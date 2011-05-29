
ENV=python-dev

# Set this on the command-line to optimise systest runtime
SYSTEST_PROCESSES=4

all: test

env:
	virtualenv --no-site-packages $(ENV)
	$(ENV)/bin/pip install argparse
	$(ENV)/bin/pip install pyYAML
	$(ENV)/bin/pip install functional
	$(ENV)/bin/pip install nose
	$(ENV)/bin/pip install PyHamcrest

clean-env:
	rm -rf $(ENV)/

env-again: clean-env env

test: unit-tests system-tests

unit-tests: clean-output-dir
	$(ENV)/bin/nosetests -A "not systest" $(test)

system-tests: clean-output-dir
	$(ENV)/bin/nosetests -A "systest" --processes 4 $(test)

wip-tests: clean-output-dir
	$(ENV)/bin/nosetests -A "wip" --no-skip $(test) || true

clean-output-dir:
	rm -rf output/


SCANNED_FILES=src testing-tools deft Makefile

continually:
	@while true; do \
	  if not make; \
	  then \
	      notify-send --icon=error --category=blog --expire-time=1000 "Deft build broken" ; \
	  fi ; \
	  inotifywait -r -qq -e modify -e delete $(SCANNED_FILES); \
	done


.PHONY: all env clean-env env-again test unit-test system-test clean-output-dir continually
