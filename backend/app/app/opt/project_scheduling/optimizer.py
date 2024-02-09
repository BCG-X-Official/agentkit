# mypy: ignore-errors
# -*- coding: utf-8 -*-
from typing import Any, Dict

import pyomo.environ as pyo
from pyomo.environ import SolverFactory


def transform_json_to_dict(tasks_json: Dict[Any, Any]) -> Dict[Any, Any]:
    TASKS = {}
    for asset, specialties in tasks_json.items():
        for specialty, details in specialties.items():
            if details["prec"] is not None:
                details["prec"] = tuple(details["prec"])
            TASKS[(asset, specialty)] = details
    return TASKS


def solver_launch(tasks: Dict[Any, Any], config: Dict[Any, Any]) -> pyo.ConcreteModel:
    tasks = transform_json_to_dict(tasks)
    model = pyo.ConcreteModel()

    # tasks is a two dimensional set of (j,m) constructed from the dictionary keys
    model.TASKS = pyo.Set(initialize=tasks.keys(), dimen=2)

    # the set of jobs is constructed from a python set
    model.JOBS = pyo.Set(initialize=list(set([j for (j, m) in model.TASKS])))

    # set of resources is constructed from a python set
    model.RESOURCES = pyo.Set(initialize=list(set([m for (j, m) in model.TASKS])))

    # the order of tasks is constructed as a cross-product of tasks and filtering
    model.TASKORDER = pyo.Set(
        initialize=model.TASKS * model.TASKS,
        dimen=4,
        filter=lambda model, j, m, k, n: (k, n) == tasks[(j, m)]["prec"],
    )
    # time points at which resource availability is checked
    model.TIMEPOINTS = pyo.Set(initialize=list(range(0, int(sum(tasks[(j, m)]["dur"] for (j, m) in tasks.keys())) + 1)))

    # the set of disjunctions is cross-product of jobs, jobs, and machines
    model.DISJUNCTIONS = pyo.Set(
        initialize=model.JOBS * model.JOBS * model.RESOURCES,
        dimen=3,
        filter=lambda model, j, k, m: j < k and (j, m) in model.TASKS and (k, m) in model.TASKS,
    )

    # variable for each task and time point that indicates whether the task is scheduled at that time
    model.scheduled = pyo.Var(model.TASKS, model.TIMEPOINTS, within=pyo.Binary)

    # load duration data into a model parameter for later access
    @model.Param(model.TASKS)
    def dur(model, j, m):
        return tasks[(j, m)]["dur"]

    @model.Param(model.TASKS, default=0)
    def resource_req(model, j, m):
        return tasks[(j, m)].get("resource_req", 0)

    @model.Param(model.RESOURCES)
    def available_resources(model, r):
        return config["available_resources"][r]

    ub = sum([model.dur[j, m] for (j, m) in model.TASKS])

    # create decision variables
    model.makespan = pyo.Var(bounds=(0, ub))
    model.start = pyo.Var(model.TASKS, bounds=(0, ub))

    # The objective to minimize. TODO: make objective function more complex
    @model.Objective(sense=pyo.minimize)
    def minimize_makespan(model):
        return model.makespan

    # Constraint to ensure all tasks are finished at the model makespan
    @model.Constraint(model.TASKS)
    def finish_tasks(model, j, m):
        return model.start[j, m] + model.dur[j, m] <= model.makespan

    # Constraint the enforces the 'preceding' requirements
    @model.Constraint(model.TASKORDER)
    def preceding(model, j, m, k, n):
        return model.start[k, n] + model.dur[k, n] <= model.start[j, m]

    # Ensures tasks on the same 'asset' don't overlap
    @model.Disjunction(model.DISJUNCTIONS)
    def no_overlap(model, j, k, m):
        return [
            model.start[j, m] + model.dur[j, m] <= model.start[k, m],
            model.start[k, m] + model.dur[k, m] <= model.start[j, m],
        ]

    @model.Constraint(model.RESOURCES, model.TIMEPOINTS)
    def resource_constraints(model, r, t):
        return (
            sum(model.resource_req[j, m] * model.scheduled[j, m, t] for (j, m) in model.TASKS if m == r)
            <= model.available_resources[r]
        )

    pyo.TransformationFactory("gdp.bigm").apply_to(model)
    SolverFactory("appsi_highs").solve(model)

    return model
