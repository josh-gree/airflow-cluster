from aws_cdk.core import Construct


class Batch(Construct):
    def __init__(self, scope: Construct, id: str, vpc, rds, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)
