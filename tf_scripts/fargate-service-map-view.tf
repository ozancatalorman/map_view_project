

# locals.tf
locals {
  service_name_map_view = "map-view"
}

# main.tf
provider "aws" {
  region = var.aws_region
}

module "map_view_fargate_service" {
  source    = "../modules/aws-ecs/fargate-service"
  providers = {
    aws = aws
  }

  project       = var.project
  environment   = var.environment
  vpc_id        = var.vpc_id
  cluster_id    = aws_ecs_cluster.this.id

  service_name      = local.service_name_data_agent
  service_port      = "8050"
  health_check_path = "/health"

  host_header       = "dev.map.view"

  desired_count          = "1"
  task_definition_cpu    = "1024"
  task_definition_memory = "8192"

  fargate_spot_capacity_base    = 1
  fargate_spot_capacity_weight  = 100
  fargate_capacity_base         = 0
  fargate_capacity_weight       = 1

  secrets = <<-SECRETS
    [
      {
        "name":  "REEF_MAP_VIEW",
        "valueFrom": "arn:aws:ssm:${var.aws_region}:${var.aws_account_id}:parameter/${var.project}/${local.service_name_map_view}/${var.environment}/reef_map_view"
      },
      {
        "name":  "REEF_MAP_VIEW_SKEY",
        "valueFrom": "arn:aws:ssm:${var.aws_region}:${var.aws_account_id}:parameter/${var.project}/${local.service_name_map_view}/${var.environment}/reef_map_view_skey"
      },
      {
        "name":  "MONDAY_API_KEY",
        "valueFrom": "arn:aws:ssm:${var.aws_region}:${var.aws_account_id}:parameter/${var.project}/${local.service_name_map_view}/${var.environment}/monday_api_key"
      }
    ]
  SECRETS

  ecr_repo = "${var.ecr_repo_base}/${local.service_name_map_view}"

  private_subnet_ids    = var.private_subnet_ids
  alb_security_group_id = var.alb_security_group_id
  alb_listener_arn      = var.alb_listener_arn
  tg_priority           = 104

  execution_role_arn = module.service_execution_role.this_iam_role_arn
  task_role_arn      = module.service_task_role.this_iam_role_arn

  log_retention_in_days = "14"
}

resource "aws_ssm_parameter" "reef_map_view" {
  name  = "/${var.project}/${local.service_name_map_view}/${var.environment}/reef_map_view"
  type  = "SecureString"
  value = "map_view_app_password"
}

resource "aws_ssm_parameter" "reef_map_view_skey" {
  name  = "/${var.project}/${local.service_name_map_view}/${var.environment}/reef_map_view_skey"
  type  = "SecureString"
  value = "map_view_app_secret_key"
}

resource "aws_ssm_parameter" "monday_api_key" {
  name  = "/${var.project}/${local.service_name_map_view}/${var.environment}/monday_api_key"
  type  = "SecureString"
  value = "your_api_key"
}

resource "aws_ecs_cluster" "this" {
  name = "${var.project}-${var.environment}-ecs-cluster"
}

module "service_execution_role" {
  source = "../modules/aws-iam-role"
  role_name = "${var.project}-${var.environment}-ecs-execution-role"
  policies = [
    "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
  ]
}

module "service_task_role" {
  source = "../modules/aws-iam-role"
  role_name = "${var.project}-${var.environment}-ecs-task-role"
  policies = [
    "arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryReadOnly",
    "arn:aws:iam::aws:policy/CloudWatchLogsFullAccess"
  ]
}
