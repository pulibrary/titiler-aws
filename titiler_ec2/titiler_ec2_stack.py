from pathlib import Path
from aws_cdk import (core, aws_ec2 as ec2, aws_iam as iam)

class TitilerEc2Stack(core.Stack):

    def __init__(self, scope: core.Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # VPC
        vpc = ec2.Vpc(self, "tiler-cdk-vpc",
            cidr="10.0.0.0/16",
            nat_gateways=0,
            subnet_configuration=[ec2.SubnetConfiguration(name="public",cidr_mask=24,subnet_type=ec2.SubnetType.PUBLIC)]
            )

        # Security Group
        sg = ec2.SecurityGroup(self, "tiler-sg",
            vpc=vpc,
            description="SecurityGroup for titiler",
            security_group_name="Tiler SecurityGroup",
            allow_all_outbound=True,
            )

        sg.add_ingress_rule(ec2.Peer.any_ipv4(),
            ec2.Port.tcp(22), "allow ssh access from anywhere")

        sg.add_ingress_rule(ec2.Peer.any_ipv4(),
            ec2.Port.tcp(80), "allow HTTP traffic from anywhere")

        sg.add_ingress_rule(ec2.Peer.any_ipv4(),
            ec2.Port.tcp(443), "allow HTTPS traffic from anywhere")

        # Role
        role = iam.Role(self, "tiler-role", assumed_by=iam.ServicePrincipal("ec2.amazonaws.com"))
        role.add_managed_policy(iam.ManagedPolicy.from_aws_managed_policy_name("AmazonS3ReadOnlyAccess"))

        # Instance
        ubuntu_linux = ec2.MachineImage.generic_linux({
            "us-east-1": "ami-03c53cb2507dda8ae",
            "us-east-2": "ami-08853a6c93b952e8b"
            })

        instance = ec2.Instance(self, "titiler-instance",
            machine_image = ubuntu_linux,
            instance_type = ec2.InstanceType("t3.micro"),
            vpc = vpc,
            vpc_subnets = ec2.SubnetSelection(subnet_type=ec2.SubnetType.PUBLIC),
            role = role,
            security_group = sg,
            key_name = 'titiler-key-pair'
            )

        # User Data
        script = Path('configure.sh').read_text()
        instance.add_user_data(script)

        # Messages after deploy
        output = core.CfnOutput(self, "WebHost_information",
            value=instance.instance_public_ip,
            description="Web server's Public IP")
