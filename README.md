# AMI-RSS

Check if an AMI family in a region has been updated. Results are then emitted as an RSS feed.

Can place output RSS XML in either a folder or an S3 bucket (and optionally setting it to public-read ACL).

## Environment variables

| Name              | Description                                                       | Default                                                 |
|-------------------|-------------------------------------------------------------------|---------------------------------------------------------|
| DEBUG             | Enable debug output in log                                        | False                                                   |
| SLEEP_SECONDS     | Number of seconds to sleep between runs                           | 86400                                                   |
| DB_TYPE           | Database type (sqlite or postgresql)                              | sqlite                                                  |
| REGION            | Region we should report on                                        | eu-west-1                                               |
| SSM_PATH          | SSM Path of AMI recommendation                                    | /aws/service/ecs/optimized-ami/amazon-linux/recommended |
| ENABLE_SLACK      | Whether to use Slack announcements                                | False                                                   |
| SLACK_WEBHOOK_URL | Slack webhook URL to emit messages to                             |                                                         |
| DB_NAME           | sqlite: path of db file, postgresql: database name                | ami-rss.db                                              |
| DB_HOST           | postgresql: hostname of database server                           |                                                         |
| DB_USER           | postgresql: username to login as                                  |                                                         |
| DB_PASSWORD       | postgresql: password for login                                    |                                                         |
| FEED_FORMAT       | Feed format to output as (rss or atom)                            | atom                                                    |
| BASE_URL          | (optional) Base URL of RSS output (blank will disable RSS output) |                                                         |
| RESULTS_FOLDER    | URI of place to save RSS feed XML (path of s3:// URI)             | /tmp/                                                   |
| S3_SET_PUBLIC_ACL | Set the S3 object for feed XML as public-read ACL                 | False                                                   |

## aws policy for user/task

This is overly broad but the permissions model for GetParameters is really twitchy.

```
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "ssm:GetParameters"
      ],
      "Resource": [
        "arn:aws:ssm:<REGION>::*"
      ]
    }
  ]
}
```
