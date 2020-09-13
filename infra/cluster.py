from aws_cdk.core import Construct


class Cluster(Construct):
    def __init__(self, scope: Construct, id: str, vpc, rds, batch, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)
