import argparse

from gaps_wrapper import SceneObject


parser = argparse.ArgumentParser()
parser.add_argument('--data_root', type=str, default='.')
parser.add_argument('--class', type=str)


opt = parser.parse_args()

