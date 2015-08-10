import re
import os

SITE_ROOT = os.path.dirname(os.path.realpath(__file__))

TEMPLATE_DIR = os.path.join(SITE_ROOT, 'templates')

LOG_TEMPLATE = u"(Doc Builder) [{project}:{version}] {msg}"

MEDIA_URL = 'https://media.readthedocs.org'
SLUMBER_API_HOST = 'https://readthedocs.org'
GLOBAL_ANALYTICS_CODE = 'UA-17997319-1'


GH_REGEXS = [
    re.compile('github.com/(.+)/(.+)(?:\.git){1}'),
    re.compile('github.com/(.+)/(.+)'),
    re.compile('github.com:(.+)/(.+).git'),
]

BB_REGEXS = [
    re.compile('bitbucket.org/(.+)/(.+)/'),
    re.compile('bitbucket.org/(.+)/(.+)'),
    re.compile('bitbucket.org:(.+)/(.+)\.git'),
]

class BuildException(Exception):
    pass
