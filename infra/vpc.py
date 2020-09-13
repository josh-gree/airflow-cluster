from aws_cdk.core import Construct, CfnOutput
from aws_cdk.aws_ec2 import Vpc as _Vpc, Peer, Port, SecurityGroup


class Vpc(Construct):
    @property
    def vpc(self):
        return self.vpc_

    @property
    def sg_rds(self):
        return self.sg_rds_

    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)
        self.vpc_ = _Vpc(self, "vpc", max_azs=2)

        # rds security group #
        ######################
        RDS_PORT = 5432
        self.sg_rds_ = SecurityGroup(self, "sg_rds", vpc=self.vpc_)
        self.sg_rds_.add_ingress_rule(
            peer=Peer.ipv4("10.0.0.0/16"), connection=Port.tcp(RDS_PORT)
        )

        private_subnets = [subnet.subnet_id for subnet in self.vpc_.private_subnets]
        public_subnets = [subnet.subnet_id for subnet in self.vpc_.public_subnets]
        sg_rds_id = self.sg_rds.security_group_id

        CfnOutput(self, "private_subnets", value=str(private_subnets))
        CfnOutput(self, "public_subnets", value=str(private_subnets))
        CfnOutput(self, "sg_rds_id", value=sg_rds_id)
