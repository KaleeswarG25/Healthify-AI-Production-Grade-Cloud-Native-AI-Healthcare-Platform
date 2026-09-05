locals {
  ecr_repositories = [
    "frontend",
    "gateway",
    "auth",
    "report",
    "ai"
  ]
}

resource "aws_ecr_repository" "healthify" {
  for_each = toset(local.ecr_repositories)

  name                 = "${var.project_name}-${each.value}"
  image_tag_mutability = "IMMUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }

  encryption_configuration {
    encryption_type = "AES256"
  }

  tags = {
    Name    = "${var.project_name}-${each.value}"
    Service = each.value
  }
}

resource "aws_ecr_lifecycle_policy" "healthify" {
  for_each = aws_ecr_repository.healthify

  repository = each.value.name

  policy = jsonencode({
    rules = [
      {
        rulePriority = 1

        description = "Keep the latest 20 images"

        selection = {
          tagStatus   = "any"
          countType   = "imageCountMoreThan"
          countNumber = 20
        }

        action = {
          type = "expire"
        }
      }
    ]
  })
}