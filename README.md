# AMI-RSS

Check if the list of AMIs has been updated. Results are then emitted as an RSS feed.

Can place output RSS XML in either a folder or an S3 bucket (and optionally setting it to public-read ACL).

## Environment variables

| Name              | Description                                         | Default                                                 |
|-------------------|-----------------------------------------------------|---------------------------------------------------------|
| DEBUG             | Enable debug output in log                          | False                                                   |
| SLEEP_SECONDS     | Number of seconds to sleep between runs             | 86400                                                   |
| DB_TYPE           | Database type (sqlite or postgresql)                | sqlite                                                  |
| REGIONS           | Comma-separated list of regions we should report on | eu-west-1,eu-west-2                                     |
| SSM_PATH          | SSM Path of AMI recommendation                      | /aws/service/ecs/optimized-ami/amazon-linux/recommended |
| SLACK_WEBHOOK_URL | Slack webhook URL to emit messages to               |                                                         |
| DB_NAME           | sqlite: path of db file, postgresql: database name  | ami-rss.db                                              |
| DB_HOST           | postgresql: hostname of database server             |                                                         |
| DB_USER           | postgresql: username to login as                    |                                                         |
| DB_PASSWORD       | postgresql: password for login                      |                                                         |

## aws policy for user/task

```
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "ssm:GetParameter"
        "ssm:GetParameters"
        "ssm:GetParametersByPath"
      ],
      "Resource": [
        "arn:aws:ssm:<REGION>::parameter/<SSM_PATH>"
      ]
    }
  ]
}
```

# workflow

loop:
  foreach region in REGIONS:
    get AMI recommendation for SSM_PATH for this region
  parse out region/AMI name/AMI ID tuples
  if any differences to most recent set of tuples in database:
    save new set to database
    make articles from all recorded sets, including their unique id from database


{
    "Parameters": [
        {
            "Name": "/aws/service/ecs/optimized-ami/amazon-linux/recommended",
            "Type": "String",
            "Value": "{\"schema_version\":1,\"image_name\":\"amzn-ami-2018.03.n-amazon-ecs-optimized\",\"image_id\":\"ami-0150b2ec056e3c3c1\",\"os\":\"Amazon Linux\",\"ecs_runtime_version\":\"Docker version 18.06.1-ce\",\"ecs_agent_version\":\"1.25.3\"}",
            "Version": 18,
            "LastModifiedDate": 1550866113.394,
            "ARN": "arn:aws:ssm:eu-west-1::parameter/aws/service/ecs/optimized-ami/amazon-linux/recommended"
        }
    ],
    "InvalidParameters": []
}

{
  "schema_version":1,
  "image_name":"amzn-ami-2018.03.n-amazon-ecs-optimized",
  "image_id":"ami-0150b2ec056e3c3c1",
  "os":"Amazon Linux",
  "ecs_runtime_version":"Docker version 18.06.1-ce",
  "ecs_agent_version":"1.25.3"
}
