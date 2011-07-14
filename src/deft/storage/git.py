
from time import localtime
from datetime import date, datetime
from fnmatch import fnmatch
import os
import stat
from dulwich.repo import Repo
from dulwich.objects import Blob, Tree, Commit
from deft.storage.memory import MemoryIO
from deft.storage.overlay import OverlayStorage
from deft.upgrade import create_upgrader


def date_of(commit):
    return date.fromtimestamp(commit.commit_time)


class GitHistory(object):
    def __init__(self, repodir, deftdir="."):
        self.repo = Repo(repodir)
        self.deftdir = deftdir
    
    def last_commit_on(self, date):
        commit_shas = [self.repo.head()]
        found = []
        
        while commit_shas:
            commit = self.repo.commit(commit_shas.pop())
            commit_date = date_of(commit)
            
            if commit_date >= date:
                commit_shas.extend(commit.parents)
                if commit_date == date:
                    found.append((commit_date, commit))
        
        return max(found, key=lambda t: t[0])[1]
    
    def __getitem__(self, commit_sha):
        commit = self.repo.commit(commit_sha)
        tree = self.repo.tree(commit.tree)
        return GitTreeStorage(self.repo, tree, self.deftdir)
    
    def at_end_of(self, date):
        commit = self.last_commit_on(date)
        tree = self.repo.tree(commit.tree)
        return GitTreeStorage(self.repo, tree, self.deftdir)


def is_subtree(tree, name):
    return tree[name][0] & mode & stat.S_IFDIR


class GitTreeStorage(object):
    def __init__(self, repo, tree, deftdir):
        self.repo = repo
        self.tree = tree
        self.deftdir = deftdir
    
    def abspath(self, relpath):
        if self.deftdir == ".":
            return relpath
        else:
            return os.path.join(self.deftdir, relpath)
    
    def exists(self, relpath):
        return self._resolve_path(relpath) is not None
    
    def isdir(self, relpath):
        return type(self._resolve_path(relpath)) == Tree
    
    def list(self, relpattern):
        "Note: partial implementation, just enough for the FeatureTracker"
        
        parent_path = os.path.dirname(relpattern)
        file_pattern = os.path.basename(relpattern)
        parent = self._resolve_path(parent_path)
        
        if parent is None:
            return []
        else:
            return [os.path.join(parent_path, name) 
                    for (name, mode, sha) in parent.iteritems() 
                    if fnmatch(name, file_pattern)]
    
    def open(self, relpath, mode="r"):
        if mode != "r":
            raise ValueError("Git storage is read-only")
        
        f = self._resolve_path(relpath)
        if type(f) == Blob:
            return MemoryIO(content=f.data)
        else:
            raise IOError(self.abspath(relpath) + " is a directory")
    
    def _resolve_path(self, relpath):
        f = self.tree
        f_is_tree = True
        
        for e in self._split_path(relpath):
            if not (type(f) is Tree and e in f):
                return None
            
            f = self._resolve(f, e)
        
        return f
    
    def _resolve(self, tree, name):
        mode, sha = tree[name]
        is_tree = mode & stat.S_IFDIR
        if is_tree:
            return self.repo.tree(sha)
        else:
            return self.repo.get_blob(sha)
    
    def _split_path(self, relpath):
        return self.abspath(relpath).split(os.sep)
    


if __name__ == '__main__':
    import sys
    from deft.tracker import UserError
    from deft.storage.historical import HistoricalBackend
    from deft.cli import CommandLineInterface
    
    commitspec = sys.argv[1]
    cli_args = sys.argv[0:1] + sys.argv[2:]
    
    try:
        git = GitHistory(".")
        cli = CommandLineInterface(HistoricalBackend(git[commitspec]), sys.stdout, sys.stderr)
        cli.run(cli_args)
    except UserError as e:
        sys.stderr.write(str(e) + "\n")
        sys.exit(1)
