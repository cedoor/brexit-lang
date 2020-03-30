#_____ GENERAL _____#

name = "brexit-lang"
region = "us-east-1"
key_name = "amazon"
vpc_security_group_id = "sg-c31adaef"   # https://console.aws.amazon.com/ec2/v2/home#SecurityGroups

#_____ EC2 _____#

ec2_ami = "ami-07ebfd5b3428b6f4d"
ec2_instance_count = 2  #1 master, n slave
ec2_instance_type = "t2.small"
