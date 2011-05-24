

deft-dev:
	virtualenv --no-site-packages deft-dev
	deft-dev/bin/pip install argparse
	deft-dev/bin/pip install pyYAML
	deft-dev/bin/pip install nose
	deft-dev/bin/pip install PyHamcrest

clean-deft-dev:
	rm -rf deft-dev/

deft-dev-again: clean-deft-dev deft-dev

test: unit-test system-test

unit-test:
	deft-dev/bin/nosetests -A "not systest"

system-test:
	deft-dev/bin/nosetests -A "systest"

.PHONY: deft-dev clean-deft-dev deft-dev-again test unit-test system-test
