try:
    from django.dispatch import Signal
    USE_SIGNALS = True
    before_build = Signal(providing_args=["version"])
    after_build = Signal(providing_args=["version"])
    before_vcs = Signal(providing_args=["version"])
    after_vcs = Signal(providing_args=["version"])
except ImportError:
    USE_SIGNALS = False

