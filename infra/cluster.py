from aws_cdk.core import Construct, RemovalPolicy
from aws_cdk.aws_s3 import Bucket


class Cluster(Construct):
    def __init__(self, scope: Construct, id: str, vpc, rds, batch, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)
