
import sys
from operator import add
from colorsys import hsv_to_rgb
import datetime
import os
from functional import scanl1
from argparse import ArgumentParser, Action
from deft.tracker import UserError
from deft.storage.git import GitStorageHistory
from deft.history import HistoricalBackend, History
from deft.warn import PrintWarnings    
from deft.formats import write_table_as_text, write_table_as_csv, write_repr



def to_color(r,g,b):
    return color.T(r=r, g=g, b=b)

def write_table_as_chart(table, args, output):
    headers = table[0]
    data = table[1:]
    
    ranges = [[row[0].toordinal(), 0] + row[1:] for row in data]
    
    xaxis = axis.X(label="/14Date",
               tic_interval=7,
               format=lambda x: "/12/a45/hR{}"+datetime.date.fromordinal(int(x)).strftime("%Y-%m-%d"))
    yaxis = axis.Y(label="/14Features",
                   tic_interval=10,
                   minor_tic_interval=5,
                   format="/12/hR%d")
    plot_area = area.T(size=(600,400),
                       x_axis=xaxis,
                       y_axis=yaxis,
                       y_range=(0,None),
                       x_grid_over_plot=True,
                       y_grid_over_plot=True)
    
    col_count = len(headers)
    for i in range(1, col_count):
        hue = float(i)/float(col_count)
        line_color = to_color(*hsv_to_rgb(hue, 1, 1))
        fill_color = to_color(*hsv_to_rgb(hue, 0.5, 1))
        
        plot_area.add_plot(range_plot.T(
                label=headers[i], 
                data=ranges, 
                min_col=i, 
                max_col=i+1,
                fill_style=fill_style.Plain(bgcolor=fill_color),
                line_style=line_style.T(color=line_color, join_style=1, cap_style=1)))
    
    output_canvas = canvas.init(fname=output, format=args.format)
    try:
        plot_area.draw(output_canvas)
    finally:
        output_canvas.close()


def data_formatter(write_table_data):
    def apply_user_specified_stacking(table, args, output):
        write_table_data(table, output)
    return apply_user_specified_stacking


Formats = {
    "text": data_formatter(write_table_as_text),
    "csv": data_formatter(write_table_as_csv),
    "repr": data_formatter(write_repr)
}

try:
    from pychart import *
    
    for format in ("pdf", "ps", "eps", "png", "svg"):
        Formats[format] = write_table_as_chart
    
    # Pychart relies on global variables and initialises them from environment variables at import time!
    theme.use_color = 1
    theme.reinitialize()
        
    DefaultFormat = "pdf"

except ImportError:
    DefaultFormat = "text"


def format_help():
    return "one of %s; defaults to %s"% (", ".join(sorted(Formats.keys())), 
                                         DefaultFormat)

class AppendSingletonLists(Action):
    def __call__(self, parser, namespace, values, option_string=None):
        getattr(namespace, self.dest).extend([[v] for v in values])

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
parser.add_argument("-f", "--format",
                    help="output format (%s)"%(format_help(),),
                    dest="format",
                    default=DefaultFormat)



def cumulative(counts):
    return list(scanl1(add, counts))

def all_zero(counts):
    return all(count == 0 for count in counts)

def count_features(tracker, bucket):
    return sum(len(list(tracker.features_with_status(s))) for s in bucket)

def bucket_counts(tracker, buckets):
    return [count_features(tracker, b) for b in buckets]

def summarise(history, commit_sha, date, buckets, warning_listener):
    try:
        tracker = history[commit_sha]
        return bucket_counts(tracker, buckets)
    except UserError as e:
        warning_listener.failed_to_load_historical_data(date=date, error=str(e))
        return [0 for b in buckets]

def as_headers(buckets):
    return [", ".join(statuses) for statuses in buckets]


def cumulative_flow(history, buckets, warning_listener):
    bucket_stack = list(reversed(buckets))
    
    summaries = [(date, summarise(history, commit_sha, date, bucket_stack, warning_listener))
                 for (date, commit_sha)
                 in sorted(history.eod_revisions().iteritems())]
    
    header_row = [["date"] + as_headers(bucket_stack)]
    data_rows = [[date] + cumulative(summary)
                 for (date, summary)
                 in summaries
                 if not all_zero(summary)]
        
    return header_row + data_rows


def main():
    warning_listener = PrintWarnings(sys.stderr, "WARNING: ")
    try:
        args = parser.parse_args()
        
        if not args.buckets:
            raise UserError("no status buckets defined")
        
        if args.format not in Formats:
            raise UserError("unknown format {format}, should be {known_formats}".format(
                    format=args.format,
                    known_formats=format_help()))
        
        history = History(GitStorageHistory(args.directory), warning_listener)
        table = cumulative_flow(history, args.buckets, warning_listener)
        Formats[args.format](table, args, sys.stdout)
        
    except UserError as e:
        sys.stderr.write(str(e))
        sys.stderr.write(os.linesep)
        sys.exit(1)
    except KeyboardInterrupt:
        pass

if __name__ == '__main__':
    main()
