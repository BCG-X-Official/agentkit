# -*- coding: utf-8 -*-
import logging
from pathlib import Path
from typing import Any

from app.core.config import settings, yaml_configs
from app.schemas.agent_schema import ActionPlan, ActionPlans, AgentAndToolsConfig, AgentConfig
from app.schemas.ingestion_schema import IngestionPipelineConfigs
from app.schemas.tool_schema import PromptInput, SqlToolConfig, ToolConfig, ToolsLibrary
from app.utils.config import Config

logger = logging.getLogger(__name__)


def get_tool_config(
    tool_name: str,
    config_values: dict[
        str,
        Any,
    ],
) -> ToolConfig:
    """Get a tool config from a tool name and config values."""
    config_values["prompt_inputs"] = [PromptInput(**item) for item in config_values.get("prompt_inputs", [])]
    match tool_name:
        case "sql_tool":
            return SqlToolConfig(**config_values)
        case _:
            return ToolConfig(**config_values)


def load_ingestion_configs() -> IngestionPipelineConfigs:
    logger.info("Loading ingestion config from yaml file...")
    ingestion_config = Config(Path(settings.PDF_TOOL_EXTRACTION_CONFIG_PATH)).read()
    return IngestionPipelineConfigs(**ingestion_config)


def get_ingestion_configs() -> IngestionPipelineConfigs:
    ingestion_config = yaml_configs.get("ingestion_config", None)
    if ingestion_config is None:
        ingestion_config = load_ingestion_configs()
        yaml_configs["ingestion_config"] = ingestion_config
    return ingestion_config


def load_agent_config() -> AgentConfig:
    """Get the agent config."""
    logger.info("Loading agent config from yaml file...")
    agent_config = Config(Path(settings.AGENT_CONFIG_PATH)).read()
    agent_config.action_plans = ActionPlans(
        action_plans={k: ActionPlan(**v) for k, v in agent_config.action_plans.items()}
    )
    agent_config.tools_library = ToolsLibrary(
        library={
            k: get_tool_config(
                k,
                v,
            )
            for k, v in agent_config.tools_library.library.items()
        }
    )
    agent_config.common = AgentAndToolsConfig(**agent_config.common)
    return AgentConfig(**agent_config)


def load_agent_config_override(partial_config: dict[str, Any]) -> AgentConfig:
    """Get the agent config and overwrite some values."""
    agent_config = get_agent_config()
    agent_config = agent_config.copy(update=partial_config)
    return agent_config


def get_agent_config() -> AgentConfig:
    agent_config = yaml_configs.get("agent_config", None)
    if agent_config is None:
        agent_config = load_agent_config()
        yaml_configs["agent_config"] = agent_config
    return agent_config
