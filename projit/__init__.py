from importlib.metadata import version as _pkg_version, PackageNotFoundError as _PKGError

try:
    __version__ = _pkg_version("projit")
except _PKGError:
    __version__ = "0.1.13"

from .utils import locate_projit_config
from .projit import projit_load
from .projit import init as projit_init
