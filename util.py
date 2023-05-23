import os
import re


class LengthException(Exception):
    def __init__(self, msg):
        self.mag = msg


def mkdir_and_chdir(path="result"):
    if not os.path.exists(path):
        os.makedirs(path)
    os.chdir(path)

    return True


def chdir(path):
    if os.path.exists(path):
        os.chdir(path)
        return True
    return False


def split_path(path):
    pattern = '/|\?|\=|&'
    path = path.strip()
    path = re.split(pattern, path)[1:]
    return path


# Return:
# group_list: a dictionary whose index is label and value is a set, the content of the set is the field who satisfies this label
# vocabulary_dict: a dictionary whose index is field and value is label
#
def group_by(labels, groups):
    labels_len = len(labels)
    groups_len = len(groups)
    if labels_len != groups_len:
        raise LengthException("the labels length is not equal to groups length")

    group_list = dict()
    vocabulary_dict = dict()

    for i in range(labels_len):
        label = labels[i]

        if label not in group_list:
            group_list[label] = set()

        group_list[label].add(groups[i])

        vocabulary_dict[groups[i]] = label

    return group_list, vocabulary_dict


