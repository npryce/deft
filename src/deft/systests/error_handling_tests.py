
from deft.systests.support import SystestEnvironment, ProcessError, systest


@systest
def test_cannot_initialise_tracker_multiple_times():
    env = SystestEnvironment()
    
    env.deft("init", "-d", "data")
    
    try:
        env.deft("init", "-d", "data")
    except ProcessError as e:
        assert "already initialised" in e.stderr

