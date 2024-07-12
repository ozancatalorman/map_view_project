locals {
  service_name_map_view = "map-view"
}

module "map_view_fargate_service" {
  source    = "../modules/aws-ecs/fargate-service"
  providers = {
    aws = aws.use2
  }

  project       = var.project
  environment   = var.environment
  vpc_id        = module.vpc.vpc_id
  cluster_id    = aws_ecs_cluster.this.id

  service_name      = local.service_name_map_view
  service_port      = "8050"
  health_check_path = "/health"

  host_header       = "dev.map-view.reefos.ai"

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
        "valueFrom": "arn:aws:ssm:${var.default_region}:${var.aws_account_id}:parameter/${var.project}/${local.service_name_map_view}/${var.environment}/reef_map_view"
      },
      {
        "name":  "REEF_MAP_VIEW_SKEY",
        "valueFrom": "arn:aws:ssm:${var.default_region}:${var.aws_account_id}:parameter/${var.project}/${local.service_name_map_view}/${var.environment}/reef_map_view_skey"
      },
      {
        "name":  "MONDAY_API_KEY",
        "valueFrom": "arn:aws:ssm:${var.default_region}:${var.aws_account_id}:parameter/${var.project}/${local.service_name_map_view}/${var.environment}/monday_api_key"
      }
    ]
  SECRETS

  ecr_repo = "${var.ecr_repo_base}/${local.service_name_map_view}"

  private_subnet_ids    = module.vpc.private_subnets
  alb_security_group_id = module.sg_alb.this_security_group_id
  alb_listener_arn      = module.alb.this_lb_default_listener
  tg_priority           = 104

  execution_role_arn = module.service_execution_role.this_iam_role_arn
  task_role_arn      = module.service_task_role.this_iam_role_arn

  log_retention_in_days = "14"
}
