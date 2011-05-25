
import sys
import os
from argparse import ArgumentParser
from deft.tracker import FeatureTracker, UserError



def _print_output(s):
    print s

def _ignore_output(s):
    pass
    

class CommandLineInterface(object):
    def __init__(self, tracker):
        self.tracker = tracker
    
    def run(self, argv):
        parser = ArgumentParser(
            prog="deft",
            description="Deft: the Distributed, Easy Feature Tracker")

        # Subparsers should inherit options defined by the parent parser, 
        # but don't seem to in argparse 1.1, so I've defined common options
        # in a separate parser
        verbosity = ArgumentParser(add_help=False)
        verbosity.add_argument("-v", "--verbose",
                               help="verbose output",
                               action="store_const",
                               dest="verbose_output",
                               const=_print_output,
                               default=_ignore_output)
        verbosity.add_argument("-q", "--quiet",
                               help="suppress all but the most important output",
                               action="store_const",
                               dest="info_output",
                               const=_ignore_output,
                               default=_print_output)
        
        tracker_configuration = ArgumentParser(add_help=False)
        tracker_configuration.add_argument("-i", "--initial-status",
                                           help="the default initial status for new features",
                                           dest="initial_status",
                                           default=None)
        
        subparsers = parser.add_subparsers()
        
        init_parser = subparsers.add_parser("init", parents=[tracker_configuration, verbosity],
                                            help="initialise an empty Deft tracker within the current directory")
        init_parser.add_argument("-d", "--data-dir",
                                 help="the directory in which features are stored",
                                 default=None,
                                 dest="datadir")
        
        configure_parser = subparsers.add_parser("configure", parents=[tracker_configuration, verbosity],
                                                 help="configure the behaviour of the tracker")
        
        create_parser = subparsers.add_parser("create",
                                              help="create a new feature and output its id")
        create_parser.add_argument("name",
                                   help="a short name for the feature")
        create_parser.add_argument("-d", "--description",
                                   help="a longer description of the feature",
                                   default="")
        create_parser.add_argument("-s", "--status",
                                   help="the initial status of the feature",
                                   default=None)
        
        list_parser = subparsers.add_parser("list",
                                            help="list tracked features in order of priority")
        list_parser.add_argument("-n", "--count",
                                 type=int,
                                 metavar="N",
                                 default=None,
                                 help="number of features to list (negative = list N lowest priority features)")
        list_parser.add_argument("-s", "--status",
                                 help="status of features to list",
                                 required=True)
        
        status_parser = subparsers.add_parser("status",
                                              help="query or change the status of a feature")
        status_parser.add_argument("feature",
                                   help="feature name",
                                   metavar="name")
        status_parser.add_argument("status",
                                   help="the new status of the feature, if changing the status",
                                   nargs="?",
                                   default=None)
        
        priority_parser = subparsers.add_parser("priority",
                                              help="query or change the priority of a feature")
        priority_parser.add_argument("feature",
                                     help="feature name",
                                     metavar="name")
        priority_parser.add_argument("priority",
                                     help="the new priority of the feature, if changing the priority",
                                     nargs="?",
                                     type=int,
                                     default=None)
        
        purge_parser = subparsers.add_parser("purge",
                                             help="delete one or more features from the working copy")
        purge_parser.add_argument("features",
                                  help="feature name",
                                  metavar="name",
                                  nargs="+")
        
        args = parser.parse_args(argv[1:])
        command = argv[1]
        
        getattr(self, "run_" + command)(args)
    
    
    def run_init(self, args):
        config = {}
        
        if args.datadir is not None:
            config['datadir'] = args.datadir
        if args.initial_status is not None:
            config['initial_status'] = args.initial_status
        
        self.tracker.init(**config)
        args.info_output("initialised Deft tracker")
    
    def run_configure(self, args):
        config = {}
        
        if args.initial_status is not None:
            config['initial_status'] = args.initial_status
        
        self.tracker.configure(**config)
    
    def run_create(self, args):
        self.tracker.create(name=args.name, 
                            status=args.status or self.tracker.initial_status,
                            description=args.description)
    
    
    def run_list(self, args):
        for f in self.tracker.features_with_status(args.status):
            print f.name
    
    
    def run_status(self, args):
        feature = self.tracker.feature_named(args.feature)
        if args.status is not None:
            self.tracker.change_status(feature, args.status)
            feature.status = args.status
        else:
            print feature.status
    
    
    def run_priority(self, args):
        feature = self.tracker.feature_named(args.feature)
        if args.priority is not None:
            self.tracker.change_priority(feature, args.priority)
        else:
            print feature.priority
    
    
    def run_purge(self, args):
        for name in args.features:
            self.tracker.purge(name)


if __name__ == "__main__":
    tracker = FeatureTracker()
    try:
        CommandLineInterface(tracker).run(sys.argv)
        tracker.save()
    except UserError as e:
        sys.stderr.write(e.message + "\n")
        sys.exit(1)
    # Unexpected exceptions pass through and Python interpreter will print the stacktrace
