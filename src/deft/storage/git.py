
from time import localtime
from datetime import date, datetime
from fnmatch import fnmatch
import os
import stat
from dulwich.repo import Repo
from dulwich.objects import Blob, Tree, Commit
from deft.storage.memory import MemoryIO


def date_of(commit):
    return date.fromtimestamp(commit.author_time)


class GitVersionedStorage(object):
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
    
    def list(self, relpattern):
        "Note: partial implementation, just enough for the FeatureTracker"
        
        parent_path = os.path.dirname(relpattern)
        file_pattern = os.path.basename(relpattern)
        parent = self._resolve_path(parent_path)
        
        if parent is None:
            raise IOError("directory " + self.abspath(parent_path) + " does not exist")
        
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
    import deft.tracker
    from deft.cli import features_to_table, write_features_as_text
    
    git = GitVersionedStorage(".")
    date = datetime.strptime(sys.argv[1], "%Y-%m-%d").date()
    
    revision = git.at_end_of(date)
    tracker = deft.tracker.load_with_storage(revision)
    
    write_features_as_text(features_to_table(tracker.all_features()), sys.stdout)
    sys.stdout.write("\n\n")
    f = tracker.feature_named("git-integration")
    sys.stdout.write(f.name)
    sys.stdout.write("\n" + ("-"*len(f.name)) + "\n\n")
    sys.stdout.write(f.description)

