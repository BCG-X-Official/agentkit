# -*- coding: utf-8 -*-
from typing import Any, Dict, Tuple

import pandas as pd
from pyomo.environ import ConcreteModel


def post_processing(model: ConcreteModel) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """Post-process by reformatting to a schedule dataframe and extracting KPI's."""
    today = pd.Timestamp.today().round("d")
    results = [
        {
            "feature": j,
            "start_dt": today + pd.to_timedelta(model.start[j, m](), "d"),
            "duration": model.dur[j, m],
            "end_dt": today + pd.to_timedelta(model.start[(j, m)]() + model.dur[j, m], "d"),
            "specialty": m,
        }
        for j, m in model.TASKS
    ]
    kpis = {
        "schedule_length": max([model.start[(j, m)]() + model.dur[j, m] for j, m in model.TASKS]),
    }

    schedule_df = pd.DataFrame(results)

    return schedule_df, kpis
