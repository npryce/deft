
import sys
import operator
from functional import scanl1
from argparse import ArgumentParser, Action
from deft.tracker import UserError
from deft.storage.git import GitHistory
from deft.storage.historical import HistoricalBackend
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
                    help="treat all the given statuses as a single bucket",
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
                    dest="format",
                    action="store_const",
                    const=CSVTableFormat,
                    default=TextTableFormat)
parser.add_argument("-u", "--unstacked",
                    dest="stacked",
                    action="store_const",
                    const=unstacked,
                    default=stacked)

warning_listener = PrintWarnings(sys.stderr, "WARNING: ")


def count_features(tracker, bucket):
    return sum(len(list(tracker.features_with_status(s))) for s in bucket)

def bucket_counts(tracker, buckets):
    return [count_features(tracker, b) for b in buckets]

def summary(git, commit_sha, date, buckets):
    try:
        tracker = HistoricalBackend(git[commit_sha]).load_tracker(warning_listener)
        return bucket_counts(tracker, buckets)
    except UserError as e:
        warning_listener.failed_to_load_historical_data(date=date, error=str(e))
        return [0 for b in buckets]


try:
    args = parser.parse_args()
    
    if not args.buckets:
        raise UserError("no status buckets defined")
    
    buckets = list(reversed(args.buckets))
    
    git = GitHistory(args.directory)
    summaries = [[date] + args.stacked(summary(git, commit_sha, date, buckets))
                 for date, commit_sha 
                 in sorted(git.eod_commits().iteritems())]
    
    args.format.save(summaries, sys.stdout)
except KeyboardInterrupt:
    pass

