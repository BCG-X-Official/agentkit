# -*- coding: utf-8 -*-
import plotly.express as px


def call_plotly(
    df,
    ship_column,
    nr_features,
    title_text,
):
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
    df,
    output_name="schedule_",
    feature_column="s",
    save=None,
    title_text="New schedule",
    time_tag="xx",
    folder_path=None,
):
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
