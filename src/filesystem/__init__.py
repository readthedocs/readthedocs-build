import fnmatch
import os


class ReadTheDocsMixin(object):

    def __init__(self, *args, **kwargs):
        super(ReadTheDocsMixin, self).__init__(*args, **kwargs)
        self.checkout_path = os.path.join(self.doc_path, 'checkouts')
        self.env_path = os.path.join(self.doc_path, 'envs')
        self.artifact_path = os.path.join(self.doc_path, 'artifacts')

        if not os.path.exists(self.doc_path):
            os.makedirs(self.doc_path)
        if not os.path.exists(self.checkout_path):
            os.makedirs(self.checkout_path)
        if not os.path.exists(self.env_path):
            os.makedirs(self.env_path)
        if not os.path.exists(self.artifact_path):
            os.makedirs(self.artifact_path)
