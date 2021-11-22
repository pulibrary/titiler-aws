# TiTiler CDK

Amazon CDK configurations for deploying TiTiler.

## Development setup

### First-time setup

* Install language dependencies with asdf or according to versions listed in [.tool-versions](/.tool-verions)

* Install aws-cdk client
  ```
  brew install aws-cdk
  ```

* Create a virtualenv on MacOS and Linux:
  ```
  python -m venv .venv
  ```

* Activate your virtualenv
  ```
  source .venv/bin/activate
  ```

* Install the required python dependencies
  ```
  pip install -r requirements.txt
  ```

### Every time setup

```
source .venv/bin/activate
pip install -r requirements.txt
```

## Deploy

1. Synthesize the CloudFormation template for this code
  ```
  cdk synth
  ```

2. Deploy the stack
  ```
  cdk deploy
  ```

To add additional dependencies, for example other CDK libraries, just add
them to your `setup.py` file and rerun the `pip install -r requirements.txt`
command.

## Useful commands

Read the [CDK documentation](https://docs.aws.amazon.com/cdk/latest/guide/cli.html)

 * `cdk deploy`      deploy this stack to your default AWS account/region
 * `cdk destroy`     delete this stack from your default AWS account/region
 * `cdk diff`        compare deployed stack with current state
 * `cdk docs`        open CDK documentation
 * `cdk ls`          list all stacks in the app
 * `cdk synth`       emits the synthesized CloudFormation template
