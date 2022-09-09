# Bitbucket Pipelines Pipe: Cloudwatch subscription filter

Creates a cloudwatch subscription filter to ship logs to Loki

## YAML Definition

Add the following snippet to the `script` section of your `bitbucket-pipelines.yml` file:

```yaml
- pipe: docker://rubarbapp/pipe-cloudwatch-subscription-filter:latest3s
  variables:
    LOGGROUP_NAME: "<string>"
    AWS_OIDC_ROLE_ARN: "<role arn>"
    # AWS_DEFAULT_REGION: '<string> # Optional
    # DESTINATION_ARN: '<string>' # Optional
    # FILTER_NAME: '<string>' # Optional
    # FILTER_PATTERN: '<string>' # Optional
```

## Variables

| Variable           | Usage                                                                                   |
| ------------------ | --------------------------------------------------------------------------------------- |
| AWS_DEFAULT_REGION | Optional. Defaults to `eu-central-1`                                                    |
| AWS_OIDC_ROLE_ARN  | The ARN of the role used for web identity federation or OIDC                            |
| DESTINATION_ARN    | Optional. Defaults to `arn:aws:lambda:eu-central-1:<AccountID>function:lambda_promtail` |
| FILTER_NAME        | Optional. Defaults to `lambdafunction_logfilter/<loggroup_name>`                        |
| FILTER_PATTERN     | Optinal. Defaults to send all logs                                                      |
| LOGGROUP_NAME      | The name of the Log-group                                                               |
