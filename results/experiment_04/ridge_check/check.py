import json, sys, time
from kt_trial.config import load_yaml
from discrimination_free import runner
stage = load_yaml("configs/experiment_04/stage_pilot2.yaml")
stage["warp"]["estimators"]["V4"] = ["twopl"]
r = runner.execute_job(dict(kind="warp", scenario="V4", N=1000, rep=1), stage, sys.argv[1], runner.stage_hash(stage))
print(r)
