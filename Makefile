
# Which version of python are we using?
python=2.7

# Set this on the command-line to select a system-test environment. One of:
#   mem     - runs system tests using in-memory storage (fast but slight risk of inaccuracy)
#   dev     - runs system tests by spawning processes and using disk storage (slow but accurate)
#   install - like 'dev' but runs out of a test installation in output/install
systest=dev

PYTHON_ENV=python$(python)-dev

PYCHART_VER=1.39

DEFT_VER:=$(shell python setup.py --version)


all: test

env: output/lib-src/PyChart-$(PYCHART_VER)
	virtualenv --python=python$(python) --no-site-packages $(PYTHON_ENV)
	$(PYTHON_ENV)/bin/pip install argparse
	$(PYTHON_ENV)/bin/pip install pyYAML
	$(PYTHON_ENV)/bin/pip install functional
	$(PYTHON_ENV)/bin/pip install dulwich
	$(PYTHON_ENV)/bin/pip install tornado
	$(PYTHON_ENV)/bin/pip install Markdown
	$(PYTHON_ENV)/bin/pip install nose
	$(PYTHON_ENV)/bin/pip install pytest
	$(PYTHON_ENV)/bin/pip install PyHamcrest
	(cd output/lib-src/PyChart-$(PYCHART_VER); ../../../$(PYTHON_ENV)/bin/python setup.py install)

output/lib-src/PyChart-$(PYCHART_VER): libs/PyChart-$(PYCHART_VER).tar.gz
	mkdir -p $(dir $@)
	rm -rf $@
	tar xz -C $(dir $@) -f $<

clean-env:
	rm -rf $(PYTHON_ENV)/

env-again: clean-env env

test: in-process-tests out-of-process-tests

clean-test-output:
		rm -rf output/testing

in-process-tests:
	DEFT_SYSTEST_ENV=$(systest) $(PYTHON_ENV)/bin/nosetests -A "not fileio" $(test)

out-of-process-tests: clean-test-output
	DEFT_SYSTEST_ENV=$(systest) $(PYTHON_ENV)/bin/nosetests -A "fileio" --processes 4 $(test)

wip-tests: clean-test-output
	$(PYTHON_ENV)/bin/nosetests -A "wip" --no-skip $(test) || true


clean-install:
	rm -rf output/install

local-install: output/install output/unpack/Deft-$(DEFT_VER)
	(cd output/unpack/Deft-$(DEFT_VER); ../../install/bin/python setup.py install)

test-install: local-install
	make out-of-process-tests systest=install

output/unpack/Deft-$(DEFT_VER): dist/Deft-$(DEFT_VER).tar.gz
	mkdir -p output/unpack
	tar xzf $< -C $(dir $@)

dist/Deft-$(DEFT_VER).tar.gz: setup.py Makefile README.rst
	$(PYTHON_ENV)/bin/python setup.py sdist

output/install: Makefile
	rm -rf build/
	$(MAKE) env PYTHON_ENV=output/install python=$(python)

dist: dist/Deft-$(DEFT_VER).tar.gz

published:
	$(PYTHON_ENV)/bin/python setup.py sdist upload

SCANNED_FILES=src testing-tools deft Makefile setup.py bin

target=in-process-tests out-of-process-tests

continually:
	@while true; do \
	  clear; \
	  if not make $(target) systest=$(systest); \
	  then \
	      notify-send --icon=error --category=blog --expire-time=250 "Deft build broken"; \
	  fi; \
	  date; \
	  inotifywait -r -qq -e modify -e delete $(SCANNED_FILES); \
	done

clean:
	rm -rf output/ build/ dist/
	find src -name '*.pyc' | xargs rm


.PHONY: all env clean-env env-again test in-process-tests out-of-process-tests 
.PHONY: clean-test-output clean-install test-install local-install dist
.PHONY: continually
