
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
def test_changing_status():
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
def test_querying_status():
    env = SystestEnvironment()
    
    env.deft("init", "-d", "data")
    env.deft("create", "a-feature")
    
    status = env.deft("status", "a-feature").stdout.strip()
    assert status == "new"
    
    env.deft("status", "a-feature", "testing")
    
    status = env.deft("status", "a-feature").stdout.strip()
    assert status == "testing"

def parse_feature_list(s):
    return [line for line in s.split("\n")[:-1]]

