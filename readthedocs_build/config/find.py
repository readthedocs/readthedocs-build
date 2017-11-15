import os


def find_all(path, filenames):
    path = os.path.abspath(path)
    for root, dirs, files in os.walk(path, topdown=True):
        dirs.sort()
        for filename in filenames:
            if filename in files:
                yield os.path.abspath(os.path.join(root, filename))


def find_one(path, filenames):
    paths = list(find_all(path, filenames))
    if paths:
        return paths[0]
    return ''
