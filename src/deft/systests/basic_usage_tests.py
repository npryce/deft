
from deft.systests.support import SystestEnvironment, systest


@systest
def test_basic_usage():
    env = SystestEnvironment()
    
    env.deft("init", "-d", "data").succeeds()
    idx = env.deft("create", "x", "--description", "description of x").stdout0().strip()
    idy = env.deft("create", "y", "--description", "description of y").stdout0().strip()
    
    features = parse_feature_list(env.deft("list", "--status", "new").stdout0())
    assert features == [(idx, "x"), (idy, "y")]
    
    env.deft("close", idx).succeeds()
    
    features = parse_feature_list(env.deft("list", "--status", "new").stdout0())
    
    assert features == [(idy, "y")]

@systest
def test_cannot_initialise_tracker_again():
    env = SystestEnvironment()
    
    env.deft("init", "-d", "data").succeeds()
    
    stderr = env.deft("init", "-d", "data").fails().stderr
    assert "already initialised" in stderr


def parse_feature_list(s):
    return [(line[0:32], line[33:]) for line in s.split("\n")[:-1]]

