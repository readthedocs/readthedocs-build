import os


def find_all(path, filename):
    path = os.path.abspath(path)
    for root, dirs, files in os.walk(path):
        if filename in files:
            yield os.path.abspath(os.path.join(root, filename))
