import os


def find_all(path, filenames):
    path = os.path.abspath(path)
    for root, dirs, files in os.walk(path):
        for filename in filenames:
            if filename in files:
                yield os.path.abspath(os.path.join(root, filename))
