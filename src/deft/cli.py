
import sys
import os
import shutil
import subprocess
from argparse import ArgumentParser
import deft.tracker



def _print_output(s):
    print s

def _ignore_output(s):
    pass
    

def with_tracker(function):
    def wrapper(self, args):
        tracker = self.backend.load()
        function(self, tracker, args)
        tracker.save()
    
    return wrapper



EditorEnvironmentVariables = ["DEFT_EDITOR", "VISUAL", "EDITOR"]

def find_editor_command():
    for v in EditorEnvironmentVariables:
        if v in os.environ:
            return os.environ[v]
    else:
        raise deft.tracker.UserError("no editor specified: one of the environment variables " + 
                                     (", ".join(EditorEnvironmentVariables)) + " must be set")

def run_editor_process(path):
    command = find_editor_command() + " " + "\"" + path + "\""
    retcode = subprocess.call(command, shell=True)
    if retcode != 0:
        raise deft.tracker.UserError("editor command failed with status " + str(retcode) + ": " + command)


class CommandLineInterface(object):
    def __init__(self, backend, editor=run_editor_process):
        self.backend = backend
        self.editor = editor
    
    def run(self, argv):
        command = argv[0]
        
        parser = ArgumentParser(
            prog="deft",
            description="Deft: the Distributed, Easy Feature Tracker")
        
        parser.add_argument("-v", "--verbose",
                               help="verbose output",
                               action="store_const",
                               dest="verbose_output",
                               const=_print_output,
                               default=_ignore_output)
        parser.add_argument("-q", "--quiet",
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
        
        subparsers = parser.add_subparsers(title="subcommands", 
                                           dest="subcommand")
        
        init_parser = subparsers.add_parser("init", parents=[tracker_configuration],
                                            help="initialise an empty Deft tracker within the current directory")
        init_parser.add_argument("-d", "--data-dir",
                                 help="the directory in which features are stored",
                                 default=None,
                                 dest="datadir")
        
        configure_parser = subparsers.add_parser("configure", parents=[tracker_configuration],
                                                 help="configure the behaviour of the tracker")
        
        create_parser = subparsers.add_parser("create", 
                                              help="create a new feature and output its id")
        create_parser.add_argument("name",
                                   help="a short name for the feature")
        create_parser.add_argument("-d", "--description",
                                   help="a longer description of the feature",
                                   default=None)
        create_parser.add_argument("-s", "--status",
                                   help="the initial status of the feature",
                                   default=None)
        
        list_parser = subparsers.add_parser("list", 
                                            help="list tracked features in order of priority")
        list_parser.add_argument("-s", "--status",
                                 help="statuses to list (lists all features if no statuses specified)",
                                 dest="statuses",
                                 nargs="+",
                                 default=[])
        
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

        priority_parser = subparsers.add_parser("description", 
                                              help="query, change or edit the long description of a feature")
        priority_parser.add_argument("feature",
                                     help="feature name",
                                     metavar="name")
        #priority_parser.add_argument("-e", "--edit",
        #                             help="edit the description",
        #                             nargs="?",
        #                             default=False,
        #                             const=True)
        #priority_parser.add_argument("description",
        #                             help="the new description of the feature, if changing the description",
        #                             nargs="?",
        #                             type=int,
        #                             default=None)
        
        purge_parser = subparsers.add_parser("purge", 
                                             help="delete one or more features from the working copy")
        purge_parser.add_argument("features",
                                  help="feature name",
                                  metavar="name",
                                  nargs="+")
        
        args = parser.parse_args(argv[1:])
        getattr(self, "run_" + args.subcommand)(args)
    
    
    def run_init(self, args):
        config = {}
        
        if args.datadir is not None:
            config['datadir'] = args.datadir
        if args.initial_status is not None:
            config['initial_status'] = args.initial_status
        
        self.backend.init(**config)
        args.info_output("initialised Deft tracker")
    
    
    @with_tracker
    def run_configure(self, tracker, args):
        config = {}
        
        if args.initial_status is not None:
            config['initial_status'] = args.initial_status
        
        tracker.configure(**config)
    
    
    @with_tracker
    def run_create(self, tracker, args):
        feature = tracker.create(name=args.name,
                                 status=args.status or tracker.initial_status,
                                 initial_description=(args.description or ""))
        
        if args.description is None:
            self.editor(feature.description_file)
    
    
    @with_tracker
    def run_list(self, tracker, args):
        def print_feature(f):
            print f.status + " " + str(f.priority) + " " + f.name
        
        if args.statuses:
            for status in args.statuses:
                for f in tracker.features_with_status(status):
                    print_feature(f)
        else:
            for f in tracker.all_features():
                print_feature(f)
    
    @with_tracker
    def run_status(self, tracker, args):
        feature = tracker.feature_named(args.feature)
        if args.status is not None:
            tracker.change_status(feature, args.status)
            feature.status = args.status
        else:
            print feature.status
    
    
    @with_tracker
    def run_priority(self, tracker, args):
        feature = tracker.feature_named(args.feature)
        if args.priority is not None:
            tracker.change_priority(feature, args.priority)
        else:
            print feature.priority
    

    @with_tracker
    def run_description(self, tracker, args):
        feature = tracker.feature_named(args.feature)
        with open(feature.description_file) as input:
            shutil.copyfileobj(input, sys.stdout)
    
    @with_tracker
    def run_purge(self, tracker, args):
        for name in args.features:
            tracker.purge(name)


if __name__ == "__main__":
    try:
        CommandLineInterface(deft.tracker).run(sys.argv)
    except deft.tracker.UserError as e:
        sys.stderr.write(str(e) + "\n")
        sys.exit(1)
    # Unexpected exceptions pass through and Python interpreter will print the stacktrace
