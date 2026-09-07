variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "ap-south-1"
}

variable "environment" {
  description = "Deployment environment"
  type        = string
  default     = "production"
}

variable "project_name" {
  description = "Project name"
  type        = string
  default     = "healthify"
}

variable "vpc_cidr" {
  description = "VPC CIDR"
  type        = string
  default     = "10.20.0.0/16"
}

variable "availability_zones" {
  description = "Availability zones"
  type        = list(string)

  default = [
    "ap-south-1a",
    "ap-south-1b",
    "ap-south-1c"
  ]
}

variable "eks_version" {
  description = "EKS Kubernetes version"
  type        = string
  default     = "1.33"
}

variable "general_instance_types" {
  description = "EC2 instance types for general EKS nodes"
  type        = list(string)

  default = [
    "t3.large"
  ]
}

variable "gpu_instance_types" {
  description = "EC2 instance types for Ollama GPU nodes"
  type        = list(string)

  default = [
    "g4dn.xlarge"
  ]
}

variable "general_min_size" {
  type    = number
  default = 2
}

variable "general_max_size" {
  type    = number
  default = 4
}

variable "general_desired_size" {
  type    = number
  default = 2
}

variable "gpu_min_size" {
  type    = number
  default = 0
}

variable "gpu_max_size" {
  type    = number
  default = 1
}

variable "gpu_desired_size" {
  type    = number
  default = 0
}

variable "rds_instance_class" {
  description = "RDS instance class"
  type        = string
  default     = "db.t4g.micro"
}

variable "rds_allocated_storage" {
  description = "RDS storage in GB"
  type        = number
  default     = 20
}

variable "rds_database_name" {
  type    = string
  default = "healthai"
}

variable "rds_username" {
  type      = string
  sensitive = true
}

variable "rds_password" {
  type      = string
  sensitive = true
}

variable "s3_bucket_name" {
  description = "Globally unique S3 bucket name"
  type        = string
}

variable "github_repository" {
  description = "GitHub repository for OIDC"
  type        = string
  default     = "KaleeswarG25/healthify_AI"
}
variable "rds_backup_retention_period" {
  default = 7
}