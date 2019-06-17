import json
import numpy as np
import os
import random


def filter_json(the_dict):
    res = {}
    for k in the_dict.keys():
        if type(the_dict[k]) is str or \
                        type(the_dict[k]) is float or \
                        type(the_dict[k]) is int or \
                        type(the_dict[k]) is list or \
                        type(the_dict[k]) is bool or \
                        the_dict[k] is None:
            res[k] = the_dict[k]
        elif type(the_dict[k]) is dict:
            res[k] = filter_json(the_dict[k])
    return res


class Config(object):
    def __init__(self, filename=None):
        # Settings
        self.config_name = filename
        self.dataset_name = 'dataset'
        self.match_model = None

        # matching files
        self.score_f = None
        self.cov_f = None
        self.load_f = None
        self.load_lb_f = None

        # Params
        self.fairness_threshold = 0.0

        # IO
        self.experiment_out_dir = 'exp_out'
        self.codec = 'UTF-8'

        # Misc
        self.random_seed = np.random.randint(1, 99999)
        self.threads = 12
        self.debug = False

        # PR4A Paramters
        self.iter_limit = np.inf

        if filename:
            self.__dict__.update(json.load(open(filename)))
        self.random = random.Random(self.random_seed)

    def to_json(self):
        return json.dumps(filter_json(self.__dict__), indent=4, sort_keys=True)

    def save_config(self, exp_dir, filename='config.json'):
        with open(os.path.join(exp_dir, filename), 'w') as fout:
            fout.write(self.to_json())
            fout.write('\n')


DefaultConfig = Config()
