
ENV=python-dev

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

test: unit-test system-test

unit-test:
	$(ENV)/bin/nosetests -A "not systest"

system-test:
	$(ENV)/bin/nosetests -A "systest"

.PHONY: all env clean-env env-again test unit-test system-test
