
import sys
import operator
from functional import scanl1
from argparse import ArgumentParser, Action
from deft.tracker import UserError
from deft.storage.git import GitStorageHistory
from deft.history import HistoricalBackend, History
from deft.warn import PrintWarnings    
from deft.formats import TextTableFormat, CSVTableFormat

class AppendSingletonLists(Action):
    def __call__(self, parser, namespace, values, option_string=None):
        getattr(namespace, self.dest).extend([[v] for v in values])



def stacked(counts):
    return list(scanl1(operator.add, counts))

def unstacked(counts):
    return counts


parser = ArgumentParser(
    prog="deft-cfd",
    description="Deft CFD: visualise tracker history as a cumulative flow diagram")
parser.add_argument("buckets",
                    help="treat each status as a bucket",
                    metavar="STATUS",
                    nargs="*",
                    action=AppendSingletonLists,
                    default=[])
parser.add_argument("-b" "--bucket",
                    help="treat all the following statuses as a single bucket",
                    dest="buckets",
                    metavar="STATUS",
                    nargs="+",
                    action="append",
                    default=[])
parser.add_argument("-d", "--tracker-directory",
                    dest="directory",
                    nargs=1,
                    default=".")
parser.add_argument("-c", "--csv",
                    help="output in CSV format (defaults to human readable text)",
                    dest="format",
                    action="store_const",
                    const=CSVTableFormat,
                    default=TextTableFormat)
parser.add_argument("-u", "--unstacked",
                    help="do not calculate stacked values " \
                         "(for piping into tools that can generate stacked charts themselves)",
                    dest="stacked",
                    action="store_const",
                    const=unstacked,
                    default=stacked)
parser.add_argument("--no-headers",
                    help="suppress the initial row of column headers",
                    dest="headers",
                    action="store_const",
                    const=False,
                    default=True)

warning_listener = PrintWarnings(sys.stderr, "WARNING: ")


def all_zero(counts):
    return all(count == 0 for count in counts)

def count_features(tracker, bucket):
    return sum(len(list(tracker.features_with_status(s))) for s in bucket)

def bucket_counts(tracker, buckets):
    return [count_features(tracker, b) for b in buckets]

def summary(history, commit_sha, date, buckets):
    try:
        tracker = history[commit_sha]
        return bucket_counts(tracker, buckets)
    except UserError as e:
        warning_listener.failed_to_load_historical_data(date=date, error=str(e))
        return [0 for b in buckets]

def as_headers(buckets):
    return [", ".join(statuses) for statuses in buckets]

try:
    args = parser.parse_args()
    
    if not args.buckets:
        raise UserError("no status buckets defined")
    
    bucket_stack = list(reversed(args.buckets))
    
    history = History(GitStorageHistory(args.directory), warning_listener)
    
    summaries = [(date, summary(history, commit_sha, date, bucket_stack))
                 for (date, commit_sha)
                 in sorted(history.eod_revisions().iteritems())]
    
    header = [["date"] + as_headers(bucket_stack)] if args.headers else []
    
    rows = [[date] + args.stacked(summary)
            for (date, summary)
            in summaries
            if not all_zero(summary)]
    
    args.format.save(header + rows, sys.stdout)

except KeyboardInterrupt:
    pass

