#!/usr/bin/env bash

. ./.aws_creds

docker build -f config/dockerfiles/web/Dockerfile -t gardeno.global-base .

$(aws ecr get-login --no-include-email --region us-west-2)

while IFS='' read -r line || [[ -n "$line" ]]; do
    VERSION=$line
done < "./src/version.txt"

docker build -t gardeno.global ./deployment/dev
docker tag gardeno.global:latest $ECS_REPOSITORY_URL:$VERSION
docker push $ECS_REPOSITORY_URL:$VERSION

CONTAINER_DEFINITIONS=$(cat ./deployment/dev/container_definitions.json | jq -c --arg VERSION "$VERSION" --arg ECS_REPOSITORY_URL "$ECS_REPOSITORY_URL" '.[0].image = $ECS_REPOSITORY_URL + ":" + $VERSION')

TASK_DEFINITION_FAMILY_AND_REVISION=$(aws ecs register-task-definition --family $ECS_TASK_DEFINITION_NAME --network-mode "awsvpc" --execution-role-arn $ECS_EXECUTION_ROLE_ARN --memory 512 --cpu 256 --requires-compatibilities "FARGATE" --container-definitions $CONTAINER_DEFINITIONS | jq -cr ".taskDefinition.taskDefinitionArn")

aws ecs update-service --cluster $ECS_CLUSTER_NAME --service $ECS_SERVICE_NAME --task-definition $TASK_DEFINITION_FAMILY_AND_REVISION