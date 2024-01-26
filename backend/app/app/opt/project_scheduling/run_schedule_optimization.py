# -*- coding: utf-8 -*-
import json
import logging
import os
from datetime import datetime
from typing import Union

import plotly
import yaml

import app.opt.project_scheduling.optimizer as op
import app.opt.project_scheduling.plots as pl
import app.opt.project_scheduling.post_processing as post

logger = logging.getLogger(__name__)


def load_config(current_dir: str, conversationId: str = None):
    try:
        config_file = (
            f"optimization_config_{conversationId}_new.json"
            if os.path.exists(os.path.join(current_dir, "config", f"optimization_config_{conversationId}_new.json"))
            else "optimization_config.json"
        )
        logger.info("Loading config file: {}".format(config_file))
        with open(os.path.join(current_dir, "config", config_file)) as f:
            CONFIG = json.load(f)
        tasks_file = (
            f"optimization_input_{conversationId}_new.json"
            if os.path.exists(os.path.join(current_dir, "config", f"optimization_input_{conversationId}_new.json"))
            else "optimization_input.json"
        )
        logger.info("Loading task file: {}".format(tasks_file))
        with open(os.path.join(current_dir, "config", tasks_file)) as f:
            TASKS = json.load(f)
        return CONFIG, TASKS
    except yaml.YAMLError as exc:
        print(exc)
        raise ValueError


def run_scheduling_opt(conversationId: str = None) -> Union[str, str]:
    # load input and config
    current_dir = os.path.dirname(os.path.realpath(__file__))
    config, tasks = load_config(current_dir=current_dir, conversationId=conversationId)

    # launch solver
    logger.info("Launching optimization run...")
    solution_model = op.solver_launch(tasks, config)

    # post-processing
    time_tag = datetime.now().strftime("%Y_%m_%d_%Hh_%MM")

    schedule_df, kpis = post.post_processing(solution_model)

    gant_figure = pl.plot_gantt_chart(
        schedule_df,
        feature_column="feature",
        save=False,
        title_text="Optimal schedule",
        time_tag=time_tag,
        folder_path=os.path.join(current_dir, "output_data/"),
        output_name="schedule_gantt",
    )
    graphJSON = plotly.io.to_json(gant_figure, pretty=True)

    return kpis, graphJSON


if __name__ == "__main__":
    logger.info(run_scheduling_opt())
