from __future__ import annotations

import os
import re
from typing import Any, MutableMapping

import toml
from rich.console import Console
from validators.utils import validator

from . import styles
from .ask import Ask

"""
All of the good stuff. This is should be the main point for app configuration.
"""

# General
CLI_HELP = """
keyvault browser is a tool for browsing and searching for secrets in Azure Key Vault.
"""

CONFIG_DIR = f"{os.getenv('HOME')}/.config/azure-keyvault-browser"
INDEX_DIR = f"{CONFIG_DIR}/index"


@validator
def keyvault_name(name: str) -> bool:
    """Validate the name of the keyvault.

    Args:
        name (str): Name of the keyvault.

    Returns:
        bool: True or False depending on the name validity.
    """

    regex = "^[a-zA-Z0-9-]{3,24}$"
    pattern = re.compile(regex)
    return pattern.match(name) is not None


def set_config(path: str) -> MutableMapping[str, Any]:
    """Create a configuration file for the client.

    Args:
        path (str): Path to the configuration file.

    Returns:
        MutableMapping[str, Any]: Configuration for the client.
    """

    config = {}
    console = Console()
    ask = Ask()

    console.print(
        "It looks like this is the first time you are using this app.. lets add some configuration before we start :smiley:\n"  # noqa: E501
    )
    config["keyvault"] = ask.question(
        f"[b][{styles.GREY}]Key Vault Name[/][/]", validation=keyvault_name
    )

    if not os.path.exists(os.path.dirname(path)):
        os.mkdir(os.path.dirname(path))

    with open(path, "w") as f:
        toml.dump(config, f)

    return toml.load(path)


def get_config(config: str | None = None) -> MutableMapping[str, Any]:
    """Retrieve or create configuration.

    Args:
        config (str | None): Path to the configuration file.

    Returns:
        MutableMapping[str, Any]: Configuration.
    """

    if config and os.path.exists(config):
        _config = toml.load(config)

    elif config and not os.path.exists(config):
        _config = set_config(config)

    else:

        config_path = f"{CONFIG_DIR}/config.toml"

        if not os.path.exists(config_path):
            _config = set_config(config_path)
        else:
            _config = toml.load(config_path)

    return _config
