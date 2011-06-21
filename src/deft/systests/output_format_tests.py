
from deft.systests.support import systest
from hamcrest import *


@systest
def can_list_features_as_human_readable_text(env):
    env.deft("init")
    env.deft("create", "alice", "--status", "new")
    env.deft("create", "bob", "--status", "being-worked-on")
    
    assert_that(env.deft("list", "--status", "new", "being-worked-on").lines,
                equal_to(["new             1 alice",
                          "being-worked-on 1 bob  "]))


@systest
def can_list_features_as_csv(env):
    env.deft("init")
    env.deft("create", "alice", "--status", "new")
    env.deft("create", "bob", "--status", "being-worked-on")
    
    assert_that(env.deft("list", "--status", "new", "being-worked-on", "--csv").lines, 
                equal_to(["new,1,alice",
                          "being-worked-on,1,bob"]))
