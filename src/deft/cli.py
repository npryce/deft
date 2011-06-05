
import sys
from functools import partial
import os
import shutil
import subprocess
from argparse import ArgumentParser
import deft.tracker



EditorEnvironmentVariables = ["DEFT_EDITOR", "VISUAL", "EDITOR"]

def find_editor_command(env):
    for v in EditorEnvironmentVariables:
        if v in env:
            return env[v]
    else:
        raise deft.tracker.UserError("no editor specified: one of the environment variables " + 
                                     (", ".join(EditorEnvironmentVariables)) + " must be set")

def run_editor_process(path):
    command = find_editor_command(os.environ) + " " + "\"" + path + "\""
    retcode = subprocess.call(command, shell=True)
    if retcode != 0:
        raise deft.tracker.UserError("editor command failed with status " + str(retcode) + ": " + command)


def with_tracker(function):
    def wrapper(self, args):
        tracker = self.backend.load_tracker()
        function(self, tracker, args)
        tracker.save()
    
    return wrapper


def _ignore_output(s):
    pass
    

class CommandLineInterface(object):
    def __init__(self, backend, out, err, editor=run_editor_process):
        self.backend = backend
        self.editor = editor
        self.out = out
        self.err = err
        
    def run(self, argv):
        command = argv[0]
        
        parser = ArgumentParser(
            prog="deft",
            description="Deft: the Distributed, Easy Feature Tracker")
        
        parser.add_argument("-v", "--verbose",
                            help="verbose output",
                            action="store_const",
                            dest="verbose_output",
                            const=self.println,
                            default=_ignore_output)
        parser.add_argument("-q", "--quiet",
                            help="suppress all but the most important output",
                            action="store_const",
                            dest="info_output",
                            const=_ignore_output,
                            default=self.println)
        
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
        create_parser.add_argument("-s", "--status",
                                   help="the initial status of the feature",
                                   default=None)
        create_parser.add_argument("-p", "--priority",
                                   help="the initial priority of the feature",
                                   type=int,
                                   default=None)
        create_parser.add_argument("-d", "--description",
                                   help="a longer description of the feature",
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

        description_parser = subparsers.add_parser("description", 
                                                   help="query, change or edit the long description of a feature")
        description_parser.add_argument("feature",
                                        help="feature name",
                                        metavar="name")
        description_parser.add_argument("-e", "--edit",
                                        help="edit the description",
                                        action="store_const",
                                        dest="edit",
                                        const=True,
                                        default=False)
        description_parser.add_argument("-f", "--file",
                                        help="print the file of the description",
                                        action="store_const",
                                        dest="file",
                                        const=True,
                                        default=False)
        description_parser.add_argument("description",
                                        help="the new description of the feature, if changing the description",
                                        nargs="?",
                                        default=None)
        
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
        
        self.backend.init_tracker(**config)
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
        
        if args.priority is not None:
            tracker.change_priority(feature, args.priority)
        
        if args.description is None:
            self.editor(feature.description_file)
    
    
    @with_tracker
    def run_list(self, tracker, args):
        if args.statuses:
            features = (f for s in args.statuses for f in tracker.features_with_status(s))
        else:
            features = tracker.all_features()
        
        format_feature_table(features, self.out)
    
    
    @with_tracker
    def run_status(self, tracker, args):
        feature = tracker.feature_named(args.feature)
        if args.status is not None:
            tracker.change_status(feature, args.status)
            feature.status = args.status
        else:
            self.println(feature.status)
    
    
    @with_tracker
    def run_priority(self, tracker, args):
        feature = tracker.feature_named(args.feature)
        if args.priority is not None:
            tracker.change_priority(feature, args.priority)
        else:
            self.println(str(feature.priority))
    
    
    @with_tracker
    def run_description(self, tracker, args):
        feature = tracker.feature_named(args.feature)
        
        if args.description is not None:
            feature.write_description(args.description)
        
        if args.edit:
            self.editor(feature.description_file)
        elif args.file:
            self.println(feature.description_file)
        elif args.description is None:
            with feature.open_description() as input:
                shutil.copyfileobj(input, self.out)
    
    
    @with_tracker
    def run_purge(self, tracker, args):
        for name in args.features:
            tracker.purge(name)
    
    def println(self, text):
        self.out.write(text)
        self.out.write(os.linesep)


def format_feature_table(features, out):
    max_elts = partial(map, max)
    alignl = "{1:<{0}}".format
    alignr = "{1:>{0}}".format
    jagged = lambda w, t: t    
    
    table = [map(str,t) for t in [(f.status, f.priority, f.name) for f in features]]
    col_widths = reduce(max_elts, [map(len,t) for t in table], (0,0,0))
    col_formatters = map(partial, (alignl, alignr, jagged), col_widths)
    formatted_table = [[col_formatters[i](row[i]) for i in range(len(row))] for row in table]
    lines = [" ".join(row) for row in formatted_table]
    
    for line in lines:
        out.write(line)
        out.write(os.linesep)
    
    


if __name__ == "__main__":
    try:
        CommandLineInterface(deft.tracker, sys.stdout, sys.stderr).run(sys.argv)
    except deft.tracker.UserError as e:
        sys.stderr.write(str(e) + "\n")
        sys.exit(1)
    # Unexpected exceptions pass through and Python interpreter will print the stacktrace
