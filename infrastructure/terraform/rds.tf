resource "aws_security_group" "rds" {
  name        = "${var.project_name}-rds-sg"
  description = "Security group for Healthify PostgreSQL RDS"
  vpc_id      = aws_vpc.healthify.id

  tags = {
    Name = "${var.project_name}-rds-sg"
  }
}


resource "aws_vpc_security_group_ingress_rule" "rds_postgres" {
  security_group_id = aws_security_group.rds.id

  description = "Allow PostgreSQL from EKS worker nodes"

  from_port = 5432
  to_port   = 5432

  ip_protocol = "tcp"

  referenced_security_group_id = aws_security_group.eks_nodes.id
}


resource "aws_vpc_security_group_egress_rule" "rds_all" {
  security_group_id = aws_security_group.rds.id

  description = "Allow outbound traffic"

  ip_protocol = "-1"

  cidr_ipv4 = "0.0.0.0/0"
}


resource "aws_db_subnet_group" "healthify" {
  name = "${var.project_name}-rds-subnet-group"

  subnet_ids = aws_subnet.private[*].id

  tags = {
    Name = "${var.project_name}-rds-subnet-group"
  }
}


resource "aws_db_instance" "healthify" {
  identifier = "${var.project_name}-postgres"

  engine         = "postgres"
  engine_version = "17"

  instance_class = var.rds_instance_class

  allocated_storage = var.rds_allocated_storage
  storage_type      = "gp3"

  db_name  = var.rds_database_name
  username = var.rds_username
  password = var.rds_password

  port = 5432

  db_subnet_group_name = aws_db_subnet_group.healthify.name

  vpc_security_group_ids = [
    aws_security_group.rds.id
  ]

  publicly_accessible = false

  storage_encrypted = true

  backup_retention_period = var.rds_backup_retention_period

  backup_window = "18:00-19:00"

  maintenance_window = "sun:19:00-sun:20:00"

  auto_minor_version_upgrade = true

  deletion_protection = false

  skip_final_snapshot = true

  copy_tags_to_snapshot = true

  multi_az = false

  apply_immediately = false

  tags = {
    Name = "${var.project_name}-postgres"
  }
}