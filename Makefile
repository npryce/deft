
# Which version of python are we using?
PYTHON=2.7

# Set this on the command-line to select a system-test environment. One of:
#   mem  - runs system tests using in-memory storage (fast but slight risk of inaccuracy)
#   real - runs system tests by spawning processes and using disk storage (slow but accurate)
systest=real

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

test: in-process-tests out-of-process-tests

clean-test-output:
		rm -rf output/testing

in-process-tests:
	DEFT_SYSTEST_ENV=$(systest) $(PYTHON_ENV)/bin/nosetests -A "not fileio" $(test)

out-of-process-tests: clean-test-output
	DEFT_SYSTEST_ENV=$(systest) $(PYTHON_ENV)/bin/nosetests -A "fileio" $(test)

wip-tests: clean-test-output
	$(PYTHON_ENV)/bin/nosetests -A "wip" --no-skip $(test) || true


clean-install:
	rm -rf output/install

test-install: clean-install output/install
	output/install/bin/python setup.py install -n

output/install: Makefile
	virtualenv -p $(PYTHON_ENV)/bin/python --never-download --no-site-packages output/install

SCANNED_FILES=src testing-tools deft Makefile

target=in-process-tests out-of-process-tests

continually:
	@while true; do \
	  clear; \
	  if not make $(target) systest=$(systest); \
	  then \
	      notify-send --icon=error --category=blog --expire-time=1000 "Deft build broken"; \
	  fi; \
	  date; \
	  inotifywait -r -qq -e modify -e delete $(SCANNED_FILES); \
	done

clean:
	rm -rf output/
	find src -name '*.pyc' | xargs rm


.PHONY: all env clean-env env-again test in-process-tests out-of-process-tests 
.PHONY: clean-test-output clean-install continually
