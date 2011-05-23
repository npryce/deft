
import sys
import os
from argparse import ArgumentParser
from deft.tracker import FeatureTracker



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
        
        subparsers = parser.add_subparsers()
        
        init_parser = subparsers.add_parser("init", parents=[verbosity],
                                            help="initialise an empty Deft tracker within the current directory")
        init_parser.add_argument("-d", "--data-dir",
                                 help="the directory in which features are stored",
                                 default=None,
                                 dest="datadir")
        
        create_parser = subparsers.add_parser("create",
                                              help="create a new feature and output its id")
        create_parser.add_argument("name",
                                   help="a short name for the feature")
        create_parser.add_argument("-d", "--description",
                                   help="a longer description of the feature",
                                   default="")
        create_parser.add_argument("-s", "--status",
                                   help="the initial status of the feature",
                                   default="new")
        
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
        
        self.tracker.init(**config)
        args.info_output("initialised Deft tracker")
    
    
    def run_create(self, args):
        self.tracker.create(name=args.name, description=args.description, status=args.status)
    
    
    def run_list(self, args):
        for f in self.tracker.list_status(args.status):
            print f.name
    
    
    def run_status(self, args):
        feature = self.tracker.feature_named(args.feature)
        feature.status = args.status
        
    def run_purge(self, args):
        for name in args.features:
            self.tracker.purge(name)


if __name__ == "__main__":
    CommandLineInterface(FeatureTracker()).run(sys.argv)
        
