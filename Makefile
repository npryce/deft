

deft-dev:
	virtualenv --no-site-packages deft-dev
	deft-dev/bin/pip install argparse
	deft-dev/bin/pip install pyYAML
	deft-dev/bin/pip install nose
	deft-dev/bin/pip install PyHamcrest

clean-deft-dev:
	rm -rf deft-dev/

deft-dev-again: clean-deft-dev deft-dev

check:
	deft-dev/bin/nosetests -d