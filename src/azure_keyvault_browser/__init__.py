import importlib.metadata
import sys

if (sys.version_info[0], sys.version_info[1]) < (3, 9):
    sys.exit("keyvault-browser requires Python 3.9 or later.")

__version__ = importlib.metadata.version("azure_keyvault_browser")
