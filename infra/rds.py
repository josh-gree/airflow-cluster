import os

from aws_cdk.core import Construct, SecretValue, CfnOutput
from aws_cdk.aws_rds import DatabaseInstance, DatabaseInstanceEngine
from aws_cdk.aws_ec2 import (
    InstanceClass,
    InstanceSize,
    InstanceType,
    SecurityGroup,
    Peer,
    Port,
    SubnetType,
)

from vpc import Vpc

PASSWORD = os.environ["RDS_PASSWORD"]
USER = os.environ["RDS_USER"]
DATABASE = os.environ["RDS_DATABASE"]
PORT = 5432


class Rds(Construct):
    def __init__(self, scope: Construct, id: str, vpc: Vpc, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        rds = DatabaseInstance(
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
            vpc_subnets={
                "subnet_type": SubnetType.PUBLIC
            },  # Anyone can access for now! REMOVE THIS
        )

        CfnOutput(
            self,
            "rds_address",
            value=f"postgres://{USER}:{PASSWORD}@{rds.db_instance_endpoint_address}:{PORT}/{DATABASE}",
        )
