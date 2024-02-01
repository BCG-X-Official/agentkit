# -*- coding: utf-8 -*-
"""Config manager."""

import logging
import os
import re
from pathlib import Path

from box import Box

from app.utils.config_utils import read_config
from app.utils.custom_yaml_loader import CustomYamlLoader

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class Config:
    """App config."""

    def __init__(
        self,
        config_path: Path,
    ):
        self._config_path = config_path

    def read(
        self,
        resolve: bool = True,
    ) -> Box:
        """Reads main config file."""
        if not (
            os.path.isfile(self._config_path)
            and os.access(
                self._config_path,
                os.R_OK,
            )
        ):
            raise FileNotFoundError(self._config_path)
        config = read_config(
            self._config_path,
            CustomYamlLoader,
        )
        if resolve:
            config = self.resolve(config)
        return config

    @classmethod
    def resolve(
        cls,
        config: Box,
        master: Box | None = None,
    ) -> Box:
        """Resolve the config file."""
        master = master or config
        for (
            k,
            v,
        ) in config.items():
            if isinstance(
                v,
                dict,
            ):
                config[k] = cls.resolve(
                    Box(v),
                    master=master,
                )
            if (
                isinstance(
                    v,
                    str,
                )
                and "(!" in v
            ):
                regexp = r"\(!(.*?)\)"
                config[k] = re.sub(
                    regexp,
                    lambda m: master.get(m.group(1)),
                    v,
                )
            if isinstance(
                v,
                list,
            ):
                for (
                    i,
                    el,
                ) in enumerate(v):
                    if isinstance(
                        el,
                        str,
                    ):
                        if "(!" in el:
                            regexp = r"\(!(.*?)\)"
                            config[k][i] = re.sub(
                                regexp,
                                lambda m: master.get(m.group(1)),
                                el,
                            )
                    elif isinstance(
                        el,
                        dict,
                    ):
                        config[k][i] = cls.resolve(
                            Box(el),
                            master=master,
                        )
        return config
