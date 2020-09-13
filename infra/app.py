import os

from vpc import Vpc
from rds import Rds
from cluster import Cluster
from batch import Batch

from aws_cdk.core import App, Environment, Stack

ACCOUNT = os.environ["ACCOUNT"]

app = App()
env = Environment(account=ACCOUNT, region="eu-west-1")

stack = Stack(app, "airflow", env=env)

vpc = Vpc(stack, "vpc")
rds = Rds(stack, "rds", vpc=vpc)
batch = Batch(stack, "batch", vpc=vpc, rds=rds)
cluster = Cluster(stack, "cluster", vpc=vpc, rds=rds, batch=batch)

app.synth()