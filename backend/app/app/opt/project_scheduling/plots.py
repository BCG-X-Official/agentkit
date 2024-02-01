# -*- coding: utf-8 -*-
from typing import Optional

import pandas as pd
import plotly.express as px


def call_plotly(
    df: pd.DataFrame,
    ship_column: str,
    nr_features: int,
    title_text: str,
) -> px.timeline:
    """Creates the plotly figure."""
    color_params = {
        "color": "specialty",
        "color_discrete_map": {
            "Specialty_1": "#f8ce50",
            "Specialty_2": "#b8c7ff",
            "Specialty_3": "#fff44f",
        },
    }

    fig = px.timeline(
        df,
        x_start="start_dt",
        x_end="end_dt",
        y=ship_column,
        hover_data=[
            "duration",
            "start_dt",
            "end_dt",
        ],
        **color_params,
    )

    fig.update_layout(
        title_text=title_text,
        height=300 + 20 * nr_features,  # 1500 before looked nice
        title_x=0.3,
    )

    fig.update_yaxes(categoryorder="category descending")

    return fig


def plot_gantt_chart(
    df: pd.DataFrame,
    output_name: str = "schedule_",
    feature_column: str = "s",
    save: Optional[bool] = None,
    title_text: str = "New schedule",
    time_tag: str = "xx",
    folder_path: str = "",
) -> px.timeline:
    nr_features = len(df[feature_column].unique())
    fig = call_plotly(
        df,
        feature_column,
        nr_features,
        title_text,
    )

    if save:
        fig.write_html(folder_path + time_tag + output_name + ".html")

    return fig
