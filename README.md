# Brexit language analysis

Language analysis of Brexit debate using Terraform and AWS EC2 instances with Spark.

Spark script simply counts the number of occurrences of a token in the articles of the various newspapers, normalizing the value based on the total number of tokens. All data we used were obtained with Python scripts on `https://github.com/cedoor/brexit-news` repository, in which for each newspaper we obtained a JSON file with a list of articles.
___

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

With the following packages installed:
- git
- python 3
- pip 3
- terraform
- aws-cli

Clone the repo and install the dependencies from npm.

```bash
git clone https://github.com/cedoor/brexit-lang.git
cd brexit-lang
pip install -r requirements.txt
```

## :video_game: Usage

Inside the main directory:

1. Create an `.env` file with the following environment variables:

```
EC2_HOSTS="ec2-0-0-0-0.compute-1.amazonaws.com ec2-0-0-0-1.compute-1.amazonaws.com"
IDENTITY_FILE_PATH="/home/pippo/.ssh/amazon.pem"
DATA_PATH="/home/pippo/Projects/BrexitLang/brexit-news/data"
DATA_FILES="indipendent.json daily_star.json the_guardian.json the_telegraph.json"
KEY_TOKENS="but although seem appear suggest suppose think sometimes often"
```
where:
* `EC2_HOSTS` is a list of AWS EC2 host URLs (cluster node URLs) obtained with Terraform (as we will see later);
* `IDENTITY_FILE_PATH` is the AWS pem file path. You can create it in `key pairs` section of AWS EC2 page;
* `DATA_PATH` is the directory path of JSON data;
* `DATA_FILES` is a list of JSON data files to analyze;
* `KEY_TOKENS` is a list of words (tokens) to analyze.

2. Run `aws configure` to save your credentials on `~/.aws/credentials` file.

3. Set your AWS parameters on `terraform.tfvars` file. In particular, you need to update `vpc_security_group_id` variable with your AWS security group ID and:
* `ec2_ami` for your Amazon machine image;
* `ec2_instance_count` for the number of cluster nodes;
* `ec2_instance_type` for the type of instances.

4. Run the following commands:

```bash
terraform init
terraform apply
bash scripts/ec2_setup.sh .env
bash scripts/start_analysis.sh .env
terraform destroy
```

Analysis results will be saved in `~/Downloads` folder as JSON file.

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
