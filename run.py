import os
from constant import *

def sh(script):
    os.system("bash -c '%s'" % script)

def get_lines(fp):
    f = open(fp, 'r')
    lines = f.readlines()
    f.close()

    return lines

def set_lines(fp, lines):
    f = open(fp, 'w')
    f.writelines(lines)
    f.close()

def update_terraform_file(instance_count, instance_type):
    lines = get_lines("terraform.tfvars")

    for i in range(0, len(lines)):
        if "ec2_instance_count =" in lines[i]:
            lines[i] = "ec2_instance_count = " + instance_count
            lines[i] += "\n"
            continue

        if "ec2_instance_type = " in lines[i]:
            lines[i] = 'ec2_instance_type = "' + instance_type + '"'
            lines[i] += "\n"
            continue

    set_lines("terraform.tfvars", lines)

def update_env_file(instance_count):
    print()
    print("Modifying .env file...")
    print("Hosts can be found in the link below")
    print("https://console.aws.amazon.com/ec2/v2/home?region=us-east-1#Instances:sort=instanceId")

    hosts = ""
    for i in range(0, int(instance_count)):
        if i == 0:
            hosts = input("Enter url of the master: ")
        else:
            hosts += " " + input("Enter url of slave number %s: " % (i))

    lines = get_lines(".env")

    for i in range(0, len(lines)):
        if "EC2_HOSTS=" in lines[i]:
            lines[i] = 'EC2_HOSTS="' + hosts + '"'
            lines[i] += "\n"
            break

    set_lines(".env", lines)

for instance_type in INSTANCE_TYPES:
    for instance_count in INSTANCE_COUNTS:
        sh("terraform init")
        
        update_terraform_file(instance_count, instance_type)
        sh("terraform apply") #has to answer "yes" here
        
        update_env_file(instance_count)
        sh("bash scripts/ec2_setup.sh .env")
        sh("bash scripts/start_analysis.sh .env > output/%s-%s_slaves.txt 2>&1" % (instance_type, instance_count))
        
        sh("terraform destroy")
        print()
        print("-----------------------------------------")
        print()

print("done")