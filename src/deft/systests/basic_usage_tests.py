
from deft.systests.support import SystestEnvironment, ProcessError, systest


@systest
def test_basic_usage():
    env = SystestEnvironment()
    
    env.deft("init", "-d", "data")
    env.deft("create", "x", "--description", "description of x")
    env.deft("create", "y", "--description", "description of y")
    
    features = parse_feature_list(env.deft("list", "--status", "new").stdout)
    assert features == ["x", "y"]
    
    env.deft("purge", "x")
    
    features = parse_feature_list(env.deft("list", "--status", "new").stdout)
    
    assert features == ["y"]


@systest
def test_recategorisation():
    env = SystestEnvironment()
    
    env.deft("init", "-d", "data")
    env.deft("create", "x")
    env.deft("create", "y")
    env.deft("status", "x", "in-progress")
    
    features = parse_feature_list(env.deft("list", "--status", "new").stdout)
    assert features == ["y"]
    
    features = parse_feature_list(env.deft("list", "--status", "in-progress").stdout)
    assert features == ["x"]
    

@systest
def test_cannot_initialise_tracker_multiple_times():
    env = SystestEnvironment()
    
    env.deft("init", "-d", "data")
    
    try:
        env.deft("init", "-d", "data")
    except ProcessError as e:
        assert "already initialised" in e.result.stderr


def parse_feature_list(s):
    return [line for line in s.split("\n")[:-1]]

