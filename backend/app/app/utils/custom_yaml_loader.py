# -*- coding: utf-8 -*-
import logging
import os
import re
from pathlib import Path
from typing import TextIO

import yaml
from box import Box

from app.utils.config_utils import read_config

logger = logging.getLogger(__name__)


# pylint: disable=too-many-ancestors
class CustomYamlLoader(yaml.FullLoader):
    """
    Add a custom constructor "!include" to the YAML loader.

    "!include" allows to read parameters in another YAML file as if it was
    the main one.
    Examples:
        To read the parameters listed in credentials.yml and assign them to
        credentials in logging.yml:
        ``credentials: !include credentials.yml``
        To call: config.credentials
    """

    def __init__(
        self,
        stream: TextIO,
    ) -> None:
        self._root = Path(stream.name).parents[0]
        super().__init__(stream)
        self.add_constructors_and_resolvers()

    def include(
        self,
        node: yaml.nodes.ScalarNode,
    ) -> Box:
        """Read yaml files as Box objects and overwrite user specific files
        Example: !include model.yml, will be overwritten by model.$USER.yml
        """
        filename = self._root / str(self.construct_scalar(node))
        return read_config(
            filename,
            loader=CustomYamlLoader,
        )

    @classmethod
    def add_constructors_and_resolvers(cls) -> None:
        """Add custom constructors and resolvers to the loader."""
        cls.add_constructor(
            "!include",
            cls.include,
        )
        # allow to use ${ENV_VARIABLE} to use environment variable in YAML read
        path_matcher = re.compile(r".*\$\{([^}^{]+)}.*")
        cls.add_implicit_resolver(
            "!path",
            path_matcher,
            None,
        )
        cls.add_constructor(
            "!path",
            _path_constructor,
        )


def _path_constructor(
    _loader: yaml.FullLoader,
    node: yaml.nodes.ScalarNode,
) -> str:
    rtn = os.path.expandvars(node.value)
    if rtn == node.value:
        raise ValueError(f"OS key {node.value} was expected, but not set.")
    return rtn
