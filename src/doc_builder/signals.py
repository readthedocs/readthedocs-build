try:
    from django.dispatch import Signal
    USE_SIGNALS = True
except ImportError:
    USE_SIGNALS = False

before_build = Signal(providing_args=["version"])
after_build = Signal(providing_args=["version"])
