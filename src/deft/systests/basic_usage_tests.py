
from deft.systests.support import SystestEnvironment, systest


@systest
def test_basic_usage():
    env = SystestEnvironment()
    
    env.deft("init", "-d", "data").succeeds()
    idx = env.deft("create", "x", "--description", "a description").stdout0().strip()
    idy = env.deft("create", "y", "--description", "a description").stdout0().strip()
    
    features = parse_feature_list(env.deft("list", "--status", "new").stdout0())
    assert features == [(idx, "x"), (idy, "y")]
    
    env.deft("close", idx).succeeds()
    
    features = parse_feature_list(env.deft("list", "--status", "new").stdout0())
    
    assert features == [(idy, "y")]

def parse_feature_list(s):
    return [(line[0:32], line[33:]) for line in s.split("\n")[:-1]]

