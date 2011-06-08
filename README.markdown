Deft: Easy Distributed Feature Tracking
=======================================

Deft is a simple distributed feature tracker (aka issue tracker, task tracker) designed to work with a distributed version control system such as Git.

Goals / Principles
------------------

* all features have status (e.g. new, in-development, ready-for-testing, ready-for-deployment)
* absolute prioritisation of features that have the same status
* store feature database alongside the code in VCS, not in another tool
* store the feature database in plain-text files that play well with VCS and diff/merge tools
* don't re-implement functionality that is already in the VCS

Getting Started
---------------

Deft is in an early stage of development so there's no convenient installer yet.  To get it up and running:

* Make sure you have [Python 2.7](http://www.python.org) and [virtualenv](http://www.virtualenv.org) installed
* Check out the repo
* Run `make env` to create a python environment for development
* Run `make` to run all the tests.
* The `dev-deft` script will run deft from the development environment, so you don't need to install anything by hand.  Run `dev-deft --help` for help.

Now read the [Quickstart Guide](https://github.com/npryce/deft/wiki/Quickstart-Guide).

Issue Tracking
--------------

Issues are tracked with [Deft itself](https://github.com/npryce/deft/tree/master/tracker).  If you want to raise issues:

* Fork the repo & check it out locally
* Follow the 'Getting Started' steps
* use the `./dev-deft` command to create a new issue
* commit the new issue
* send a pull request

Yes... there should be a tool to make this process simpler and easy for a project's users to do.
