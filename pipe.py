# /usr/bin/env python
import boto3
import configparser
import stat
import os
import time
from bitbucket_pipes_toolkit import Pipe

schema = {
    'DESTINATION_ARN': {
        'required': False,
        'type': 'string'
    },
    'FILTER_NAME': {
        'required': False,
        'type': 'string'
    },
    'LOGGROUP_NAME': {
        'required': True,
        'type': 'string'
    },
    'FILTER_PATTERN': {
        'required': False,
        'type': 'string'
    },
    'AWS_DEFAULT_REGION': {
        'type': 'string',
        'required': False
    },
    'AWS_OIDC_ROLE_ARN': {
        'type': 'string',
        'required': True
    },
    'BITBUCKET_STEP_OIDC_TOKEN': {
        'type': 'string',
        'required': True
    }
}


class SubscriptionPipe(Pipe):

    def auth(self):
        web_identity_token = os.getenv('BITBUCKET_STEP_OIDC_TOKEN')
        random_number = str(time.time_ns())
        aws_config_directory = os.path.join(os.environ["HOME"], '.aws')
        oidc_token_directory = os.path.join(
            aws_config_directory, '.aws-oidc')

        os.makedirs(aws_config_directory, exist_ok=True)
        os.makedirs(oidc_token_directory, exist_ok=True)

        web_identity_token_path = os.path.join(
            f'{aws_config_directory}/.aws-oidc', f'oidc_token_{random_number}')
        with open(web_identity_token_path, 'w') as f:
            f.write(self.get_variable('BITBUCKET_STEP_OIDC_TOKEN'))
        os.chmod(web_identity_token_path, mode=stat.S_IRUSR)

        pipe.log_info('Web identity token file is created')

        aws_configfile_path = os.path.join(aws_config_directory, 'config')
        with open(aws_configfile_path, 'w') as configfile:
            config = configparser.ConfigParser()
            config['default'] = {
                'role_arn': self.get_variable('AWS_OIDC_ROLE_ARN'),
                'web_identity_token_file': web_identity_token_path
            }
            config.write(configfile)
        pipe.log_info(
            'Configured settings for authentication with assume web identity role')

    def run(self):
        super().run()
        self.auth()

        cloudwatch_client = boto3.client('logs', region_name='eu-central-1')
        sts_client = boto3.client('sts', region_name='eu-central-1')

        account_id = sts_client.get_caller_identity()

        loggroup_name = self.get_variable('LOGGROUP_NAME')

        if self.get_variable('DESTINATION_ARN'):
            destination_arn = self.get_variable('DESTINATION_ARN')
        else:
            destination_arn = 'arn:aws:lambda:eu-central-1:' + \
                account_id['Account'] + ':function:lambda_promtail'

        if self.get_variable('FILTER_NAME'):
            filter_name = self.get_variable('FILTER_NAME')
        else:
            filter_name = 'lambdafunction_logfilter' + loggroup_name

        if self.get_variable('AWS_DEFAULT_REGION'):
            aws_default_region = self.get_variable('AWS_DEFAULT_REGION')
        else:
            aws_default_region = "eu-central-1"

        if self.get_variable('FILTER_PATTERN'):
            filter_pattern = self.get_variable('FILTER_PATTERN')
        else:
            filter_pattern = " "

        pipe.log_info('Our account_id is ' + account_id['Account'])

        paginator = cloudwatch_client.get_paginator(
            'describe_subscription_filters')
        for response in paginator.paginate(logGroupName=loggroup_name):
            if response['subscriptionFilters'] == []:
                pipe.log_info("creating " + filter_name +
                              " filter for " + loggroup_name)
                cloudwatch_client.put_subscription_filter(
                    destinationArn=destination_arn,
                    filterName=filter_name,
                    filterPattern=" ",
                    logGroupName=loggroup_name
                )
            else:
                pipe.log_info("Logs for " + loggroup_name +
                              " are already sent to " + destination_arn)


pipe_metadata = {
    'name': 'pipe-cloudwatch-subscription-filter',
}

pipe = SubscriptionPipe(pipe_metadata=pipe_metadata, schema=schema)
pipe.run()
