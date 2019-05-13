import matplotlib as mlp
mlp.use('Agg')
import matplotlib.pyplot as plt

import argparse
import numpy as np
import os

from plot.plotting_style import BORDER_COLOR, LABEL_COLOR

from util.Config import Config


if __name__ == '__main__':
    """Create paper score boxplots for an assignment of papers to reviewers.

    For each paper, compute its _paper score_ by summing the affinities of the 
    reviewers assigned to it. Sort the paper scores for each paper in ascending
    order. Divide the sorted scores into 5 equal groups. Plot a boxplot fo each
    group.
    
    Args:
      config_dirs - a space separated list of directories (probably within 
      exp_out/ each of which corresponding to a matching run (and containing the
      corresponding config file).
    
    Return:
      Saves a boxplot per input directory within the input directory inside a 
      directory called results (which also contains the results of matching).
    """
    parser = argparse.ArgumentParser(description='Create paper score boxplot.')
    parser.add_argument('config_dirs', type=str, nargs='+',
                        help='path to exp_out config')
    args = parser.parse_args()

    num_quantiles = 5
    for config_dir in args.config_dirs:
        # Initialize.
        config = Config(os.path.join(config_dir, 'config.json'))
        scores = np.load(config.score_f)
        assignment = np.load(os.path.join(config_dir, 'results',
                                          'assignment.npy'))
        match_scores = np.sum(assignment * scores, axis=0)
        max_possible = np.max(scores) * np.max(np.sum(assignment, axis=0))
        sorted_scores = sorted(match_scores)
        num_papers = np.size(sorted_scores)
        scores_per_quant = int(np.floor(num_papers / num_quantiles) + 1)
        quants = []
        for i in range(num_quantiles):
            if i != num_quantiles - 1:
                quants.append(
                    sorted_scores[i * scores_per_quant:
                                  (i + 1) * scores_per_quant])
            else:
                quants.append(sorted_scores[i * scores_per_quant:])

        # Create Figure.
        fig, ax = plt.subplots(1, 1)
        bps = ax.boxplot(quants, 0, 'rx')
        ax.set_title(config.match_model)
        ax.set_ylabel('Paper Score')
        ax.set_xlabel('Quintile')
        ax.set_ylim(bottom=0.0, top=max_possible)

        # Change borders, tick colors, etc.
        ax.spines['bottom'].set_color(BORDER_COLOR)
        ax.spines['left'].set_color(BORDER_COLOR)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.tick_params(axis='x', which='both', bottom=True, top=False,
                       color=BORDER_COLOR)
        ax.tick_params(axis='y', which='both', left=True, right=False,
                       color=BORDER_COLOR)
        ax.xaxis.label.set_color(LABEL_COLOR)
        ax.yaxis.label.set_color(LABEL_COLOR)
        for l in ax.xaxis.get_ticklabels():
            l.set_color(LABEL_COLOR)
        for l in ax.yaxis.get_ticklabels():
            l.set_color(LABEL_COLOR)

        out_dir = os.path.join(config_dir, 'results', '%s-box-%s.png' %
                               (config.dataset_name, config.match_model))
        fig.savefig(out_dir)
