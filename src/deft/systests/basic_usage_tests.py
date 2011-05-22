
from deft.systests.support import SystestEnvironment, systest


@systest
def test_basic_usage():
    env = SystestEnvironment()
    
    env.deft("init", "-d", "data").succeeds()
    env.deft("create", "x", "--description", "description of x").succeeds()
    env.deft("create", "y", "--description", "description of y").succeeds()
    
    features = parse_feature_list(env.deft("list", "--status", "new").stdout0())
    assert features == ["x", "y"]
    
    env.deft("close", "x").succeeds()
    
    features = parse_feature_list(env.deft("list", "--status", "new").stdout0())
    
    assert features == ["y"]

@systest
def test_cannot_initialise_tracker_multiple_times():
    env = SystestEnvironment()
    
    env.deft("init", "-d", "data").succeeds()
    
    stderr = env.deft("init", "-d", "data").fails().stderr
    assert "already initialised" in stderr


def parse_feature_list(s):
    return [line for line in s.split("\n")[:-1]]

