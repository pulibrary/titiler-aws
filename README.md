# TiTiler CDK

Amazon CDK configurations for deploying TiTiler.

## First-time setup

* Install language dependencies with asdf or according to versions listed in [.tool-versions](/.tool-verions)

* Install aws-cdk client
  ```
  brew install aws-cdk
  ```

* Install pipenv
  ```
  pip install --user pipenv
  ```

* Install the required python dependencies
  ```
  pipenv sync
  ```

* Activate your virtualenv
  ```
  pipenv shell
  ```

* Update your `.aws/config` to include:
  ```
  [titiler-deploy]
  region = us-east-1
  ```

* Update your `.aws/credentials` to include credentials from LastPass -> Shared-ITIMS-Passwords\Figgy -> TiTilerAWS like
  ```
  [titiler-deploy]
  aws_access_key_id = [username]
  aws_secret_access_key = [password]
  ```

* Copy `.env.example` to `.env` and update the account number using the note from that LastPass entry.


## Every time setup

```
pipenv sync
pipenv shell
```

## Check that changes are valid

```
cdk synth
```

## Deploy TiTiler

1. Deploy the staging stack
  ```
  cdk --profile titiler-deploy deploy titiler-staging
  ```

1. Deploy the production stack
  ```
  cdk --profile titiler-deploy deploy titiler-production
  ```

To add additional dependencies, for example other CDK libraries, just add
them with the `pipenv install` command.

## Useful commands

Read the [CDK documentation](https://docs.aws.amazon.com/cdk/latest/guide/cli.html)

 * `cdk deploy`      deploy this stack to your default AWS account/region
 * `cdk destroy`     delete this stack from your default AWS account/region
 * `cdk diff`        compare deployed stack with current state
 * `cdk docs`        open CDK documentation
 * `cdk ls`          list all stacks in the app
 * `cdk synth`       emits the synthesized CloudFormation template
