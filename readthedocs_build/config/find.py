import os
import re


def find_all(path, filename_regex):
    path = os.path.abspath(path)
    for root, dirs, files in os.walk(path, topdown=True):
        dirs.sort()
        for filename in files:
            if re.match(filename_regex, filename):
                yield os.path.abspath(os.path.join(root, filename))


def find_one(path, filename_regex):
    for _path in find_all(path, filename_regex):
        return _path
    return ''
