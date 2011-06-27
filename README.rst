Deft: Easy Distributed Feature Tracking
=======================================

Deft is a simple distributed feature tracker (aka issue tracker,
task tracker, bug tracker) designed to work with a distributed
version control system such as Git.

Principles
----------


-  All features have a status (e.g. new, in-development,
   ready-for-testing, ready-for-deployment)
-  Absolute prioritisation of features that have the same status
-  Store feature database alongside the code in VCS, not in another
   tool
-  Store the feature database in plain-text files that play well
   with VCS and diff/merge tools
-  Don't re-implement functionality that is already in the VCS

Getting Started
---------------

Install from `PyPI`_ using easy\_install or pip. For example:

::

    % pip install deft

After that you can use the ``deft`` command to create, manipulate
and query Deft feature trackers. Use ``deft --help`` and/or read
the `Quickstart Guide`_ to get started.

Reporting Issues and Feature Requests
-------------------------------------

Issues are tracked with `Deft itself`_.
If you want to raise issues or feature requests:


-  Fork the repo & check it out locally
-  Follow the 'Developing Deft' steps
-  use the ``./dev-deft`` command to create a new issue
-  commit the new issue
-  send a pull request

Yes... there should be a tool to make this process simpler and easy
for a project's users to do.

Developing Deft
---------------

To work on the Deft code itself:


-  You need `Python 2.7`_ and `virtualenv`_ installed
-  Check out from `GitHub`_
-  Run ``make env`` to create a python environment for development
-  Run ``make`` to run all the tests.
-  The ``dev-deft`` script will run deft from the development
   environment. Run ``dev-deft --help`` for help.


.. _PyPI: http://pypi.python.org/pypi/Deft
.. _Quickstart Guide: https://github.com/npryce/deft/wiki/Quickstart-Guide
.. _Deft itself: https://github.com/npryce/deft/tree/master/tracker
.. _Python 2.7: http://www.python.org
.. _virtualenv: http://www.virtualenv.org
.. _GitHub: http://github.com/npryce/deft
