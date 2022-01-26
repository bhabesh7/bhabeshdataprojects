# The data set used in this example is from http://archive.ics.uci.edu/ml/datasets/Wine+Quality
# P. Cortez, A. Cerdeira, F. Almeida, T. Matos and J. Reis.
# Modeling wine preferences by data mining from physicochemical properties. In Decision Support Systems, Elsevier, 47(4):547-553, 2009.

# from asyncio.windows_events import NULL
import os
import warnings
import sys

import pandas as pd
import numpy as np
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.linear_model import ElasticNet
from urllib.parse import urlparse
import mlflow
import mlflow.sklearn
from mlflow.tracking.client import MlflowClient
import logging
import json

logging.basicConfig(level=logging.WARN)
logger = logging.getLogger(__name__)


class WineTrain:
    def __init__(self, mlflowObj, experimentid, runname, isregister, modelnametoberegistered):
        self._mlflowObj = mlflowObj
        self._experimentid = experimentid
        self._runname = runname
        self._isregister = isregister
        self._modelnametoberegistered = modelnametoberegistered

    def eval_metrics(self, actual, pred):
        rmse = np.sqrt(mean_squared_error(actual, pred))
        mae = mean_absolute_error(actual, pred)
        r2 = r2_score(actual, pred)
        return rmse, mae, r2

    # if __name__ == "__main__":
    def trigger_training(self):
        try:
            warnings.filterwarnings("ignore")
            np.random.seed(40)

            # Read the wine-quality csv file from the URL
            csv_url = (
                "http://archive.ics.uci.edu/ml/machine-learning-databases/wine-quality/winequality-red.csv"
            )
            try:
                data = pd.read_csv(csv_url, sep=";")
            except Exception as e:
                logger.exception(
                    "Unable to download training & test CSV, check your internet connection. Error: %s", e
                )

            # Split the data into training and test sets. (0.75, 0.25) split.
            train, test = train_test_split(data)

            # The predicted column is "quality" which is a scalar from [3, 9]
            train_x = train.drop(["quality"], axis=1)
            test_x = test.drop(["quality"], axis=1)
            train_y = train[["quality"]]
            test_y = test[["quality"]]

            # bhabesh - for test data generation
            test_x_df = pd.DataFrame(data=test_x).to_json(orient='split')

            alpha = float(sys.argv[1]) if len(sys.argv) > 1 else 0.5
            l1_ratio = float(sys.argv[2]) if len(sys.argv) > 2 else 0.5

            # with mlflow.start_run(run_id="8d53f8bb2af84c3dae07032ae6492f79"):
            # mlflow.set_experiment("iris")
            # mlflow.set_tracking_uri("sqlite:///mydb.sqlite")

            with self._mlflowObj.start_run():
                lr = ElasticNet(alpha=alpha, l1_ratio=l1_ratio, random_state=42)
                lr.fit(train_x, train_y)

                predicted_qualities = lr.predict(test_x)

                (rmse, mae, r2) = self.eval_metrics(test_y, predicted_qualities)

                print("Elasticnet model (alpha=%f, l1_ratio=%f):" % (alpha, l1_ratio))
                print("  RMSE: %s" % rmse)
                print("  MAE: %s" % mae)
                print("  R2: %s" % r2)

                mlflow.log_param("alpha", alpha)
                mlflow.log_param("l1_ratio", l1_ratio)
                mlflow.log_metric("rmse", rmse)
                mlflow.log_metric("r2", r2)
                mlflow.log_metric("mae", mae)

                # tags
                mlflow.set_tag("alarm_name", "alarm_sp")
                mlflow.set_tag("alarm_id", "5556")

                tracking_url_type_store = urlparse(mlflow.get_tracking_uri()).scheme

                # artifacturl = mlflow.get_artifact_uri()
                print("end")
                # mlflowClient = MlflowClient(tracking_url="sqlite:///mydb.sqlite")
                # mlflow.log_artifacts()
                if not self._isregister:
                    return

                if not self._modelnametoberegistered:
                    print("model name to be registered is empty. Please pass a valid name")
                    return
                # Model registry does not work with file store
                if tracking_url_type_store != "file":

                    # Register the model
                    # There are other ways to use the Model Registry, which depends on the use case,
                    # please refer to the doc for more information:
                    # https://mlflow.org/docs/latest/model-registry.html#api-workflow
                    # this line doesnt work with file:
                    # mlflow.sklearn.log_model(lr, "model", registered_model_name=self._modelnametoberegistered)
                    self._mlflowObj.sklearn.log_model(lr, "model", registered_model_name=self._modelnametoberegistered)
                else:
                    # mlflow.sklearn.log_model(lr, "model")
                    self._mlflowObj.sklearn.log_model(lr, "model")

                # Basically there are 3 ways to regoster model in model registry
                # from mlflow.tracking import MlflowClient
                # mlflowclient = MlflowClient(tracking_uri="sqlite:///mydb.sqlite")
                # # create an empty model first
                # model_lookedup = mlflowclient.get_registered_model("ElasticnetWineModel_2")
                # if(model_lookedup is NULL):
                #     reg_model = mlflowclient.create_registered_model("ElasticnetWineModel_2")

                # result = mlflowclient.create_model_version(name="ElasticnetWineModel_2", source="mlruns/0/8d53f8bb2af84c3dae07032ae6492f79/artifacts/sklearn-model", run_id="8d53f8bb2af84c3dae07032ae6492f79")

                # print(result)

                # technique 2
                # mlflow.register_model("runs:/d16076a3ec534311817565e6527539c0/sklearn-model","ElasticnetWineModel_2")
        except Exception as ex:
            print("error during training: {}".format(ex))
        finally:
            self._mlflowObj.end_run()