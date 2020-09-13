from aws_cdk.core import Construct, Duration, CfnOutput
from aws_cdk.aws_ecs import (
    Cluster as _Cluster,
    FargateService,
    FargateTaskDefinition,
    ContainerImage,
    LogDriver,
    PortMapping,
)
from aws_cdk.aws_ec2 import (
    Vpc as _Vpc,
    InstanceSize,
    InstanceType,
    InstanceClass,
)
from aws_cdk.aws_elasticloadbalancingv2 import ApplicationLoadBalancer, HealthCheck

from vpc import Vpc
from rds import Rds


class InitTask(Construct):
    def __init__(
        self, scope: Construct, id: str, shared_airflow_env: dict, **kwargs
    ) -> None:
        super().__init__(scope, id, **kwargs)
        task_definition = FargateTaskDefinition(
            self,
            "initdb",
            cpu=512,
            memory_limit_mib=1024,
        )
        task_definition.add_container(
            "initdb",
            image=ContainerImage.from_registry("apache/airflow:1.10.12-python3.8"),
            command=["initdb"],
            logging=LogDriver.aws_logs(stream_prefix="initdb"),
            environment=shared_airflow_env,
        )

        CfnOutput(self, "init-task-def", value=task_definition.task_definition_arn)


class WebserverService(Construct):
    def __init__(
        self,
        scope: Construct,
        id: str,
        cluster: _Cluster,
        shared_airflow_env: dict,
        vpc: _Vpc,
        **kwargs,
    ) -> None:
        super().__init__(scope, id, **kwargs)
        task_definition = FargateTaskDefinition(
            self, "task-def", cpu=512, memory_limit_mib=1024
        )
        container = task_definition.add_container(
            "container",
            image=ContainerImage.from_registry("apache/airflow:1.10.12-python3.8"),
            command=["webserver"],
            logging=LogDriver.aws_logs(stream_prefix="webserver"),
            environment=shared_airflow_env,
        )

        port_mapping = PortMapping(container_port=8080, host_port=8080)
        container.add_port_mappings(port_mapping)

        service = FargateService(
            self,
            "service",
            cluster=cluster,
            task_definition=task_definition,
        )

        lb = ApplicationLoadBalancer(self, "lb", vpc=vpc, internet_facing=True)
        listener = lb.add_listener("public_listener", port=80, open=True)

        health_check = HealthCheck(
            interval=Duration.seconds(60),
            path="/health",
            timeout=Duration.seconds(5),
        )

        listener.add_targets(
            "webserver",
            port=8080,
            targets=[service],
            health_check=health_check,
        )

        CfnOutput(self, "LoadBalancerDNS", value=lb.load_balancer_dns_name)


class SchedulerService(Construct):
    def __init__(
        self,
        scope: Construct,
        id: str,
        cluster: _Cluster,
        shared_airflow_env: dict,
        **kwargs,
    ) -> None:
        super().__init__(scope, id, **kwargs)
        task_definition = FargateTaskDefinition(
            self,
            "task-def",
            cpu=512,
            memory_limit_mib=1024,
        )

        task_definition.add_container(
            "container",
            image=ContainerImage.from_registry("apache/airflow:1.10.12-python3.8"),
            command=["scheduler"],
            logging=LogDriver.aws_logs(stream_prefix="scheduler"),
            environment=shared_airflow_env,
        )

        FargateService(
            self,
            "service",
            cluster=cluster,
            task_definition=task_definition,
        )


class Cluster(Construct):
    def __init__(
        self, scope: Construct, id: str, vpc: Vpc, rds: Rds, batch, **kwargs
    ) -> None:
        super().__init__(scope, id, **kwargs)

        cluster = _Cluster(self, "cluster", vpc=vpc.vpc)

        cluster.add_capacity(
            "ag",
            instance_type=InstanceType.of(InstanceClass.STANDARD5, InstanceSize.LARGE),
        )

        shared_airflow_env = {
            "AIRFLOW__CORE__SQL_ALCHEMY_CONN": rds.uri,
            "AIRFLOW__CORE__LOAD_EXAMPLES": "True",
            "AIRFLOW__CORE__EXECUTOR": "LocalExecutor",
        }

        init_db = InitTask(self, "init_db", shared_airflow_env=shared_airflow_env)

        scheduler_service = SchedulerService(
            self,
            "scheduler_service",
            cluster=cluster,
            shared_airflow_env=shared_airflow_env,
        )

        webserver_service = WebserverService(
            self,
            "webserver_service",
            cluster=cluster,
            shared_airflow_env=shared_airflow_env,
            vpc=vpc.vpc,
        )

        CfnOutput(self, "cluster-name", value=cluster.cluster_name)