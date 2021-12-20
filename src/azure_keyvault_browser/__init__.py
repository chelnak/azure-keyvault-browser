import sys

if (sys.version_info[0], sys.version_info[1]) < (3, 7):
    sys.exit("azure-keyvault-browser requires Python 3.7 or later.")

try:
    import importlib.metadata

    __version__ = importlib.metadata.version("azure_keyvault_browser")
except ModuleNotFoundError:
    import importlib_metadata

    __version__ = importlib_metadata.version("azure_keyvault_browser")
