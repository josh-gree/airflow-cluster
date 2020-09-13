from aws_cdk.core import Construct, RemovalPolicy
from aws_cdk.aws_s3 import Bucket


class Vpc(Construct):
    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)
        b = Bucket(self, "b", removal_policy=RemovalPolicy.DESTROY)
