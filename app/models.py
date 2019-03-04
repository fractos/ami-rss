import json

from logzero import logger

class Record:
    """
    Holds the fields associated with a record

    {
        "schema_version": 1,
        "image_name": "amzn-ami-2018.03.n-amazon-ecs-optimized",
        "image_id": "ami-0150b2ec056e3c3c1",
        "os": "Amazon Linux",
        "ecs_runtime_version": "Docker version 18.06.1-ce",
        "ecs_agent_version": "1.25.3"
    }
    """

    def __init__(self, id="", timestamp="", region="", row="", image_name="", image_id="", os="", ecs_runtime_version="", ecs_agent_version=""):
        if len(id) > 0:
            self.id = id

        if len(timestamp) > 0:
            self.timestamp = timestamp

        if len(region) > 0:
            self.region = region

        if row:
            row_dict = dict(row)
            logger.debug(f"row: {json.dumps(row_dict)}")
            if "id" in row_dict:
                logger.debug("setting id to " + row_dict["id"])
                self.id = row_dict["id"]

            if "timestamp" in row_dict:
                self.timestamp = row_dict["timestamp"]

            if "region" in row_dict:
                self.region = row_dict["region"]

            self.image_name = row_dict["image_name"]
            self.image_id = row_dict["image_id"]
            self.os = row_dict["os"]
            self.ecs_runtime_version = row_dict["ecs_runtime_version"]
            self.ecs_agent_version = row_dict["ecs_agent_version"]
        else:
            self.image_name = image_name
            self.image_id = image_id
            self.os = os
            self.ecs_runtime_version = ecs_runtime_version
            self.ecs_agent_version = ecs_agent_version


    def as_dict(self):
        return {
            "id": self.id,
            "timestamp": self.timestamp,
            "region": self.region,
            "image_name": self.image_name,
            "image_id": self.image_id,
            "os": self.os,
            "ecs_runtime_version": self.ecs_runtime_version,
            "ecs_agent_version": self.ecs_agent_version
        }


    def get_content(self):
        return f"AMI for {self.image_name} ({self.image_id}) is now available for {self.os} in {self.region}. It has ECS runtime version {self.ecs_runtime_version} and ECS agent version {self.ecs_agent_version}."
