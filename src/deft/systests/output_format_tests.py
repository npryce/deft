
from deft.systests.support import systest
from hamcrest import *


@systest
def can_create_new_features(env):
    env.deft("init")
    env.deft("create", "alice", "--status", "new")
    env.deft("create", "bob", "--status", "being-worked-on")
    
    assert_that(env.deft("list", "--status", "new", "being-worked-on").lines, equal_to([
                    "new             1 alice",
                    "being-worked-on 1 bob"]))
