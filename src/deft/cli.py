
import sys
from functools import partial
import os
import shutil
import csv
import yaml
import subprocess
from argparse import ArgumentParser, Action
import deft.tracker
from deft.tracker import UserError


EditorEnvironmentVariables = ["DEFT_EDITOR", "VISUAL", "EDITOR"]

def find_editor_command(env):
    for v in EditorEnvironmentVariables:
        if v in env:
            return env[v]
    else:
        raise UserError("no editor specified: one of the environment variables " + 
                        (", ".join(EditorEnvironmentVariables)) + " must be set")

def run_editor_process(path):
    command = find_editor_command(os.environ) + " " + "\"" + path + "\""
    retcode = subprocess.call(command, shell=True)
    if retcode != 0:
        raise UserError("editor command failed with status " + str(retcode) + ": " + command)


def with_tracker(function):
    def wrapper(self, args):
        tracker = self.backend.load_tracker()
        function(self, tracker, args)
        tracker.save()
    
    return wrapper


def _ignore_output(s):
    pass
    




def append_value(namespace, name, value):
    values = getattr(namespace, name) or []
    values = values + [value]
    setattr(namespace, name, values)

class AppendPropertySetter(Action):
    def __call__(self, parser, namespace, values, option_string=None):
        def setter(properties):
            properties[values[0]] = values[1]
        
        append_value(namespace, self.dest, setter)

class AppendPropertyDeleter(Action):
    def __call__(self, parser, namespace, values, option_string=None):
        def deleter(properties):
            del properties[values[0]]
        
        append_value(namespace, self.dest, deleter)


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
        create_parser.add_argument("-t", "--set",
                                   help="set a property of the feature",
                                   dest="properties",
                                   metavar=("NAME", "VALUE"),
                                   action="append",
                                   nargs=2,
                                   default=[])
        
        list_parser = subparsers.add_parser("list", 
                                            help="list tracked features in order of priority")
        list_parser.add_argument("-s", "--status",
                                 help="statuses to list (lists all features if no statuses specified)",
                                 dest="statuses",
                                 metavar="STATUS",
                                 nargs="+",
                                 default=[])
        list_parser.add_argument("-p", "--properties",
                                 help="properties to show for each feature",
                                 metavar="NAME",
                                 dest="properties",
                                 default=[],
                                 nargs="+")
        list_parser.add_argument("-c", "--csv",
                                 help="output in CSV format (default is human-readable text)",
                                 dest="format",
                                 action="store_const",
                                 const="csv",
                                 default="text")
        
        statuses_parser = subparsers.add_parser("statuses",
                                                help="list all active statuses")
        
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
        
        properties_parser = subparsers.add_parser("properties", 
                                                  help="query, change or edit the properties of a feature")
        properties_parser.add_argument("feature",
                                       help="feature name",
                                       metavar="feature")
        properties_parser.add_argument("-e", "--edit",
                                       help="edit the properties in YAML format (see http://www.yaml.org)",
                                       action="store_const",
                                       dest="edit",
                                       const=True,
                                       default=False)
        properties_parser.add_argument("-f", "--file",
                                       help="print the file of the properties",
                                       action="store_const",
                                       dest="file",
                                       const=True,
                                       default=False)
        properties_parser.add_argument("-s", "--set",
                                       help="set a property value",
                                       metavar=("NAME", "VALUE"),
                                       action=AppendPropertySetter,
                                       dest="changes",
                                       nargs=2)
        properties_parser.add_argument("-r", "--remove",
                                       help="remove a property from the feature",
                                       metavar="NAME",
                                       action=AppendPropertyDeleter,
                                       dest="changes",
                                       nargs=1)
        properties_parser.add_argument("-p", "--print",
                                       help="properties to query",
                                       dest="properties_to_print",
                                       default=None,
                                       nargs="+")
        
        rename_parser = subparsers.add_parser("rename",
                                              help="rename a feature")
        rename_parser.add_argument("feature",
                                   help="the current name of the feature",
                                   metavar="FROM-NAME")
        rename_parser.add_argument("new_name",
                                   help="the new name of the feature",
                                   metavar="TO-NAME")
        
        purge_parser = subparsers.add_parser("purge", 
                                             help="delete one or more features from the working copy")
        purge_parser.add_argument("features",
                                  help="feature name",
                                  metavar="name",
                                  nargs="+")
        
        upgrade_parser = subparsers.add_parser("upgrade-format",
                                               help="upgrade the tracker database to the format "
                                                    "supported by this version of the software")
        
        args = parser.parse_args(argv[1:])
        getattr(self, "run_" + args.subcommand.replace("-", "_"))(args)
    
    
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
                                 status=args.status or None,
                                 description=(args.description or ""),
                                 properties=dict(args.properties))
        
        if args.priority is not None:
            feature.priority = args.priority
        
        if args.description is None:
            self.editor(feature.description_file)
            
    
    @with_tracker
    def run_statuses(self, tracker, args):
        for s in tracker.statuses:
            self.println(s)
    
    @with_tracker
    def run_list(self, tracker, args):
        if args.statuses:
            features = (f for s in args.statuses for f in tracker.features_with_status(s))
        else:
            features = tracker.all_features()
        
        table = features_to_table(features, args.properties)
        
        if args.format == "text":
            write_features_as_text(table, self.out)
        elif args.format == "csv":
            write_features_as_csv(table, self.out)
        else:
            raise ValueError("unexpected format: " + args.format)
    
    @with_tracker
    def run_status(self, tracker, args):
        feature = tracker.feature_named(args.feature)
        if args.status is not None:
            feature.status = args.status
        else:
            self.println(feature.status)
    
    @with_tracker
    def run_priority(self, tracker, args):
        feature = tracker.feature_named(args.feature)
        if args.priority is not None:
            feature.priority = args.priority
        else:
            self.println(str(feature.priority))
    
    @with_tracker
    def run_description(self, tracker, args):
        feature = tracker.feature_named(args.feature)
        
        if args.description is not None:
            feature.description = args.description
        
        if args.edit:
            self.editor(feature.description_file)
        elif args.file:
            self.println(feature.description_file)
        elif args.description is None:
            self.out.write(feature.description)
    
    @with_tracker
    def run_properties(self, tracker, args):
        feature = tracker.feature_named(args.feature)
        
        if args.edit:
            self.editor(feature.properties_file)
        elif args.file:
            self.println(feature.properties_file)
        else:
            properties = feature.properties
            if args.changes:
                for change in args.changes:
                    change(properties)
                feature.properties = properties
            else:
                if args.properties_to_print:
                    for key in args.properties_to_print:
                        if key in properties:
                            self.println(properties[key])
                        else:
                            raise UserError("feature " + feature.name + " does not have a property named " + repr(key))
                elif properties:
                    deft.tracker.YamlFormat.save(properties, self.out)
    
    @with_tracker
    def run_rename(self, tracker, args):
        feature = tracker.feature_named(args.feature)
        feature.name = args.new_name
    
    @with_tracker
    def run_purge(self, tracker, args):
        for name in args.features:
            tracker.purge(name)
    
    def run_upgrade_format(self, args):
        from deft.upgrade import upgrade
        upgrade(self.backend.tracker_storage())
        
    
    def println(self, text):
        self.out.write(text)
        self.out.write(os.linesep)


def property_values(feature, names):
    if names:
        properties = feature.properties
        return [properties.get(name, "") for name in names]
    else:
        return []

def features_to_table(features, property_names=[]):
    return [tuple([f.status, f.priority, f.name] + property_values(f, property_names)) for f in features]


def write_features_as_text(features_table, out):
    if not features_table:
        return
    
    max_elts = partial(map, max)
    
    alignl = "{1:<{0}}".format
    alignr = "{1:>{0}}".format
    def align_for(v):
        return alignr if type(v) == int else alignl

    table = [map(str,t) for t in features_table]
    zeros = [0 for elt in features_table[0]]
    aligns = [align_for(v) for v in features_table[0]]
    col_widths = reduce(max_elts, [map(len,t) for t in table], zeros)
    col_formatters = map(partial, aligns, col_widths)
    formatted_table = [[col_formatters[i](row[i]) for i in range(len(row))] for row in table]
    lines = [" ".join(row) for row in formatted_table]
    
    for line in lines:
        out.write(line)
        out.write(os.linesep)


def write_features_as_csv(features_table, out):
    csv_out = csv.writer(out)
    csv_out.writerows(features_table)


def main():
    try:
        CommandLineInterface(deft.tracker, sys.stdout, sys.stderr).run(sys.argv)
    except deft.tracker.UserError as e:
        sys.stderr.write(str(e) + "\n")
        sys.exit(1)
    # Unexpected exceptions pass through and Python interpreter will print the stacktrace
