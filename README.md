# Brexit language analysis

Language analysis of Brexit debate using Terraform and AWS EC2 instances with Spark.

Spark scripts counts the number of occurrences of a token in the articles of the various newspapers, normalizing the value based on the total number of tokens. In addition, two models are trained with logistic regression, one to distinguish whether an article is for or against Brexit, the other to distinguish whether an article talks about Brexit or not.

All data we used were obtained with Python scripts on [brexit-news](https://github.com/epilurzu/brexit-news) repository, in which for each newspaper we obtained a JSON file with a list of articles.

________________________________

## :paperclip: Table of Contents
- :hammer: [Install](#hammer-install)
- :video_game: [Usage](#video_game-usage)
- :chart_with_upwards_trend: [Development](#chart_with_upwards_trend-development)
  - :scroll: [Rules](#scroll-rules)
    - [Commits](#commits)
    - [Branches](#branches)
- :page_facing_up: [License](#page_facing_up-license)
- :telephone_receiver: [Contacts](#telephone_receiver-contacts)
  - :boy: [Developers](#boy-developers)

## :hammer: Install

You must have the following packages installed on the system:
- git
- [terraform](https://learn.hashicorp.com/terraform/getting-started/install)
- [aws-cli](https://docs.aws.amazon.com/cli/latest/userguide/install-cliv2-linux.html)

And clone the repo:

```bash
git clone https://github.com/cedoor/brexit-lang.git
cd brexit-lang
```

## :video_game: Usage

### AWS parameters

Inside the main directory (`brexit-lang`):

1. Run `aws configure` to save your credentials on local `~/.aws/credentials` file. The command interactively asks some parameters, it's important to set the following: AWS Access Key ID, AWS Secret Access Key. If you have an aws educated student account, you should find your credentials on the vocareum page by clicking on `Account Detail`.

2. Set your AWS parameters on `terraform.tfvars` file within the `brexit-lang` folder:
* `vpc_security_group_id` (**must be changed**): You need to set your AWS security group ID conteined in [security group section](https://console.aws.amazon.com/ec2/v2/home#SecurityGroups:sort=group-id), on the EC2 service page;
* `ec2_instance_count`: number of cluster nodes (default: `2`);
* `ec2_instance_type`: the type of node instances (default: `t2.small`).


Security group must contain the right `inbound rules` to enable user access with ssh. For example :

|    Type     |    Protocol   |  Port range  |   Source     |
|-------------|:-------------:|:------------:|:------------:|
| All traffic |      All      |     All      |  0.0.0.0/0 * |

\* **Attention to security, this is just an example!**

To run the code as it should, other parameters **must not** be changed. For instance, **do not change** parameters like:
* `region`: AWS region (value: `us-east-1`);
* `ec2_ami`: Amazon machine image (value: `ami-07ebfd5b3428b6f4d`, Ubuntu Server 18.04 LTS);
* `key_name`: Name of identity pem file (value: `amazon.pem`)

### Create instances

To create EC2 instances run the following commands:

```bash
terraform init
terraform apply
```

When `terraform apply` command execution ends and prints the cluster instance information, you will set the DNS of the cluster istances created in `EC2_HOSTS` environment variable as explained below.

It is now necessary to create a file called `.env` and update the following environment variables as described below:

```
EC2_HOSTS="ec2-0-0-0-0.compute-1.amazonaws.com ec2-0-0-0-1.compute-1.amazonaws.com"
IDENTITY_FILE_PATH="/home/pippo/.ssh/amazon.pem"
DATA_PATH="/home/pippo/Projects/BrexitLang/brexit-news/data"
LEAVER_NEWSPAPER_FILES="daily_star.json the_telegraph.json the_sun.json"
REMAIN_NEWSPAPER_FILES="indipendent.json the_guardian.json daily_mirror.json"
NEUTRAL_NEWSPAPER_FILE="the_new_york_times.json"
KEY_TOKENS="but although seem appear suggest suppose think sometimes often usually likelihood assumption possibility likely unlikely conceivable conceivably probable probably roughly sort they could would we"
```

where:

* `EC2_HOSTS` is a list of AWS EC2 hosts URLs (cluster node URLs) obtained with `terraform apply` command. The first one must be the master. You can also find created instances on the [AWS page](https://console.aws.amazon.com/ec2/v2/home#Instances:sort=instanceId);
* `IDENTITY_FILE_PATH` is the AWS pem file path. You can create it in key pairs [section of AWS EC2 page](https://console.aws.amazon.com/ec2/v2/home#KeyPairs). It is important to call this file `amazon.pem` and run `chmod 600 amazon.pem` to give the right permissions;
* `DATA_PATH` is the directory path of JSON data with newspaper articles (it should only contain the files listed below);
* `LEAVER_NEWSPAPER_FILES` is a list of JSON data files of leaver newspapers. 
* `REMAIN_NEWSPAPER_FILES` is a list of JSON data files of remain newspapers.
* `NEUTRAL_NEWSPAPER_FILE` is a JSON data file of a neutral newspaper (it does not mention Brexit).
* `KEY_TOKENS` is a list of words (tokens) to analyze.

All the data files has to be in the following format:
```json
{"title": "article title", "url": "article url", "timestamp": 1540252800000, "content": "article body"}
{"title": "article title", "url": "article url", "timestamp": 1540228613000, "content": "article body"}
{"title": "article title", "url": "article url", "timestamp": 1522188456900, "content": "article body"}
```

### Setup cluster

After the creation of the instances, check again that the paths on the `.env` file are correct and setup all the nodes with the following command:

```bash
bash scripts/setup_instances.sh .env
```

This command installs Java, Python dependencies, Hadoop and Spark. Then, set up the cluster and upload the data to HDFS. At this point you can run the script for analysis or classification.

### Analysis

Analysis script get the `KEY_TOKENS` values and all the newspapers, and counts the number of occurrences of the tokens in the articles of each newspaper, normalizing the value based on the total number of newspaper tokens. 

You can run the script with the following command:

```bash
bash scripts/start_analysis.sh .env
```

Analysis results will be saved in local `~/Downloads` folder as JSON file called `analysis_results.json`.

### Classification

In the classification script two models are trained with logistic regression, one to distinguish whether an article is for or against Brexit, the other to distinguish whether an article talks about Brexit or not. The first model uses all Brexit newspapers to train except the last one, which it uses to create an additional separate test set. The second model uses all Brexit newspapers except the last one and the neutral newspaper. The script saves the accuracies of the two models in the resulting file.

You can run the script with the following command:

```bash
bash scripts/start_classification.sh .env
```

Classification results will be saved in local `~/Downloads` folder as JSON file called `classification_results.json`.

### Destroy instances

Finally, to destroy instances from AWS run the following command:

```bash
terraform destroy
```

At this point if you want you can do another analysis with a new cluster.

### Stop and start instances

Unfortunately there is still no terraform command to stop or start instances. However, it is possible to use `aws-cli` with the following commands:

```bash
aws ec2 stop-instances --region us-east-1 --instance-ids <ids>
aws ec2 start-instances --region us-east-1 --instance-ids <ids>
```

## :chart_with_upwards_trend: Development

### :scroll: Rules

#### Commits

* Use this commit message format (angular style):  

    `[<type>] <subject>`
    `<BLANK LINE>`
    `<body>`

    where `type` must be one of the following:

    - feat: A new feature
    - fix: A bug fix
    - docs: Documentation only changes
    - style: Changes that do not affect the meaning of the code
    - refactor: A code change that neither fixes a bug nor adds a feature
    - test: Adding missing or correcting existing tests
    - chore: Changes to the build process or auxiliary tools and libraries such as documentation generation
    - update: Update of the library version or of the dependencies

and `body` must be should include the motivation for the change and contrast this with previous behavior (do not add body if the commit is trivial). 

* Use the imperative, present tense: "change" not "changed" nor "changes".
* Don't capitalize first letter.
* No dot (.) at the end.

#### Branches

* There is a master branch, used only for release.
* There is a dev branch, used to merge all sub dev branch.
* Avoid long descriptive names for long-lived branches.
* No CamelCase.
* Use grouping tokens (words) at the beginning of your branch names (in a similar way to the `type` of commit).
* Define and use short lead tokens to differentiate branches in a way that is meaningful to your workflow.
* Use slashes to separate parts of your branch names.
* Remove branch after merge if it is not important.

Examples:
    
    git branch -b docs/README
    git branch -b test/one-function
    git branch -b feat/side-bar
    git branch -b style/header

## :page_facing_up: License
* See [LICENSE](https://github.com/cedoor/brexit-lang/blob/master/LICENSE) file.

## :telephone_receiver: Contacts
### :boy: Developers

#### Cedoor
* E-mail : me@cedoor.dev
* Github : [@cedoor](https://github.com/cedoor)
* Website : https://cedoor.dev

#### Epilurzu
* E-mail : e.ipodda@gmail.com
* Github : [@epilurzu](https://github.com/epilurzu)
