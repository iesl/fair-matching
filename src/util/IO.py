import errno
import os
from shutil import copytree


def mkdir_p(filepath):
    try:
        os.makedirs(filepath)
    except OSError as exc:
        if exc.errno != errno.EEXIST:
            raise
        pass


def copy_source_to_dir(output_dir, config):
    try:
        os.makedirs(output_dir)
        # save the source code.
        copytree(os.path.join(os.environ['MATCH_ROOT'], 'src'),
                 os.path.join(output_dir, 'src'))
        copytree(os.path.join(os.environ['MATCH_ROOT'], 'bin'),
                 os.path.join(output_dir, 'bin'))
        copytree(os.path.join(os.environ['MATCH_ROOT'], 'config'),
                 os.path.join(output_dir, 'config'))

        # save the config to outdir.
        config.save_config(output_dir)

    except OSError as e:
        if e.errno != errno.EEXIST:
            print('%s already exists' % output_dir)
