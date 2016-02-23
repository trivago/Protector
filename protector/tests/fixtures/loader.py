import os


def load_fixture(name):
    path = os.path.dirname(os.path.abspath(__file__))
    urls_file = "{}/{}".format(path, name)
    return open(urls_file)
