import subprocess


def run(args):
    popen = subprocess.Popen(args)
    return popen.wait()
