import os

from aws_cdk.core import Construct, SecretValue, CfnOutput
from aws_cdk.aws_rds import DatabaseInstance, DatabaseInstanceEngine
from aws_cdk.aws_ec2 import (
    InstanceClass,
    InstanceSize,
    InstanceType,
)
from aws_cdk.aws_ssm import StringListParameter

from vpc import Vpc

PASSWORD = os.environ["RDS_PASSWORD"]
USER = os.environ["RDS_USER"]
DATABASE = os.environ["RDS_DATABASE"]
PORT = 5432


class Rds(Construct):
    @property
    def uri(self):
        return f"postgres://{USER}:{PASSWORD}@{self.rds.db_instance_endpoint_address}:{PORT}/{DATABASE}"

    def __init__(self, scope: Construct, id: str, vpc: Vpc, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        self.rds = DatabaseInstance(
            self,
            "rds",
            master_username=USER,
            master_user_password=SecretValue(PASSWORD),
            database_name=DATABASE,
            vpc=vpc.vpc,
            engine=DatabaseInstanceEngine.POSTGRES,
            port=PORT,
            instance_type=InstanceType.of(InstanceClass.BURSTABLE3, InstanceSize.MICRO),
            security_groups=[vpc.sg_rds],
            deletion_protection=False,
        )

        CfnOutput(
            self,
            "rds_address",
            value=f"postgres://{USER}:{PASSWORD}@{self.rds.db_instance_endpoint_address}:{PORT}/{DATABASE}",
        )
