# -*- coding: utf-8 -*-
import getpass
import logging
import os
from pathlib import Path
from typing import Optional, Type

import yaml
from box import Box

logger = logging.getLogger(__name__)


def read_config(
    filename: Path,
    loader: Type[yaml.FullLoader],
) -> Box:
    config = _read_config(
        filename,
        loader=loader,
    )
    _overwrite_config_with_user_specific_file(
        config,
        filename=filename,
        loader=loader,
    )
    return config


def _overwrite_config_with_user_specific_file(
    config: Box,
    filename: Path,
    loader: Type[yaml.FullLoader],
) -> None:
    """Overwrite the config files with user specific files."""
    user_filename = _user_specific_file(filename)
    if user_filename is not None:
        logger.info(f"{filename} overwritten by {user_filename}")
        user_config: Box = _read_config(
            user_filename,
            loader=loader,
        )
        config.merge_update(user_config)


def _user_specific_file(
    file_path: Path,
) -> Optional[Path]:
    """
    Find user specific files for a filename.

    E.g. user_specific_file(config.yml) = config.$USER.yml if the file
    exists, else returns None
    """
    username = (
        getpass.getuser()
        .lower()
        .replace(
            " ",
            "_",
        )
    )
    user_filename = Path(file_path).with_suffix(f".{username}{file_path.suffix}")
    if user_filename.is_file() and os.access(
        user_filename,
        os.R_OK,
    ):
        return user_filename
    return None


def _read_config(
    file_path: Path,
    loader: Type[yaml.FullLoader],
) -> Box:
    """Read any yaml file as a Box object."""

    if file_path.is_file() and os.access(
        file_path,
        os.R_OK,
    ):
        with open(
            file_path,
            "r",
            encoding="utf-8",
        ) as f:
            try:
                config_dict = yaml.load(
                    f,
                    Loader=loader,
                )
            except yaml.YAMLError as exc:
                print(exc)
        return Box(
            config_dict,
            box_dots=True,
        )
    raise FileNotFoundError(file_path)
