[
  {
    "name": "aea-agent-runner",
    "image": "${ecr_repository_url}:latest",
    "cpu": 512,
    "memory": 1024,
    "essential": true,
    "portMappings": [
      {
        "containerPort": 8080,
        "hostPort": 8080,
        "protocol": "tcp"
      }
    ],
    "environment": [
      {
        "name": "AEA_AUTONOMOUS_LOOP_ENABLED",
        "value": "true"
      },
      {
        "name": "AEA_AGENT_PORT",
        "value": "8080"
      }
    ],
    "secrets": [
      {
        "name": "GITLAB_TOKEN",
        "valueFrom": "${gitlab_token_secret_arn}"
      }
    ],
    "logConfiguration": {
      "logDriver": "awslogs",
      "options": {
        "awslogs-group": "/ecs/aea-agent-runner",
        "awslogs-region": "${aws_region}",
        "awslogs-stream-prefix": "ecs"
      }
    }
  }
]
