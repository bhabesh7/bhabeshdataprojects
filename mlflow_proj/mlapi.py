import requests
from requestmanager import RequestManager
import mlflow
import mlflow.sklearn
from mlflow.tracking.client import MlflowClient

from winetrain import WineTrain

MLFLOW_URL = "http://localhost:5000/"
TRACKING_URL = "sqlite:///mlflowdb.sqlite"


class Mlapi:
    def __init__(self):
        self.mlflowClient = MlflowClient(tracking_uri=TRACKING_URL)
        mlflow.set_tracking_uri(TRACKING_URL)

    def createexperiment(self, experimentname):
        experiment = None
        if experimentname is None:
            return
        try:
            experiment = self.mlflowClient.get_experiment_by_name(experimentname)
        except:
            # experiment = self.mlflow.create_experiment(experimentname)
            print("fetch experiment attempt - none found with the name {}".format(experimentname))
        mlflow.set_experiment(experimentname)
        return experiment

    def createrun(self, experimentname, experimentid, runname, isregister, modelnametoberegistered):
        # with mlflow.start_run(experiment_id=experimentid, run_name=runname):
        winetrainobj = WineTrain(mlflow, experimentid, runname, isregister, modelnametoberegistered)
        winetrainobj.trigger_training()

    def get_experiment_by_name(self, experimentname):
        try:
            experiment = self.mlflowClient.get_experiment_by_name(experimentname)
        except():
            print("error while fetching experiment {}".format(experimentname))
        return experiment

    def get_runs_from_experiment(self, experimentid):
        runinfos = self.mlflowClient.list_run_infos(experiment_id=experimentid)
        return runinfos

    def get_run_info(self, runid):
        pass

    def get_registered_model_by_name(self, modelname):
        registered_model = None
        try:
            registered_model = self.mlflowClient.get_registered_model(name=modelname)
        except Exception as ex:
            print(ex)
        return registered_model
