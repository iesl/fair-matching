"""Run the basic matcher us LP solver."""
import argparse
import datetime
import numpy as np
import os
import random
import time

from models.FairIR import FairIR

from util.Config import Config
from util.IO import mkdir_p, copy_source_to_dir

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Solve paper matching with FairIR.')
    parser.add_argument('config', type=str, help='config file.')
    args = parser.parse_args()

    # Load data & initialize
    config = Config(args.config)
    loads = np.load(config.load_f)
    covs = np.load(config.cov_f)
    scores = np.load(config.score_f)
    if config.load_lb_f:
        loads_lb = np.load(config.load_lb_f)
    else:
        loads_lb = None
    rand = random.Random(config.random_seed)
    config.random = rand
    print('#info random seed %s' % config.random_seed)
    debug = config.debug
    fairness_threshold = config.fairness_threshold
    assert(config.match_model == 'fairir' or
           config.match_model == 'fairir-lb')

    # Set up output dir
    now = datetime.datetime.now()
    ts = "{:04d}-{:02d}-{:02d}-{:02d}-{:02d}-{:02d}".format(
        now.year, now.month, now.day, now.hour, now.minute, now.second)
    config.experiment_out_dir = os.path.join(
        config.experiment_out_dir, config.dataset_name, config.match_model, ts)
    output_dir = config.experiment_out_dir
    print('#info output-dir %s' % output_dir)
    copy_source_to_dir(output_dir, config)
    output_dir = os.path.join(output_dir, 'results')
    mkdir_p(output_dir)

    # Solve.
    mm = FairIR(loads, loads_lb, covs, scores, fairness_threshold)
    s = time.time()
    mm.solve()
    t = time.time() - s

    # Output files.
    assignment_file = os.path.join(output_dir, 'assignment')
    time_file = os.path.join(output_dir, 'time.tsv')
    obj_file = os.path.join(output_dir, 'obj.tsv')
    makespan_file = os.path.join(output_dir, 'makespan.tsv')

    with open(obj_file, 'w') as f:
        f.write(str(mm.objective_val()))
    with open(time_file, 'w') as f:
        f.write(str(t))
    with open(makespan_file, 'w') as f:
        f.write('%s' % mm.makespan)
    np.save(assignment_file, mm.sol_as_mat())
    print('#info objective %s' % mm.objective_val())
