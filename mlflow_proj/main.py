# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
from mlapi import Mlapi

def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}')  # Press Ctrl+F8 to toggle the breakpoint.


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    print_hi('PyCharm - MLflow project to create experiment, runs, log models and retrieve info')
    experiment_name ="bca_exp"
    mlapiObj = Mlapi()
    # step 1: create experiment
    # experiment = mlapiObj.createexperiment(experiment_name)

    #step 2: get created experiment
    experiment = mlapiObj.get_experiment_by_name(experiment_name)
    print(experiment)
    if experiment is None:
        exit(1)

    #step 3: invoke some mltraining code which creates a run & log metrics/params in te experiment + register model option
    MODEL_NAME_TO_BE_REGISTERED = "wine_lr_model"
    mlapiObj.createrun(experiment.name, experiment.experiment_id, "testrun_jan_26", True, MODEL_NAME_TO_BE_REGISTERED)

    #step 4: fetch the run info from mlflow
    run_infos = mlapiObj.get_runs_from_experiment(experimentid=experiment.experiment_id)
    [print(run) for run in run_infos]

    registered_model = mlapiObj.get_registered_model_by_name(MODEL_NAME_TO_BE_REGISTERED)
    print(registered_model)

    print("Exiting Program after success")

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
