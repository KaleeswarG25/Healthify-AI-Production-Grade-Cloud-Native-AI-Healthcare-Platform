output "vpc_id" {
  value = aws_vpc.healthify.id
}

output "private_subnet_ids" {
  value = aws_subnet.private[*].id
}

output "public_subnet_ids" {
  value = aws_subnet.public[*].id
}

output "eks_cluster_name" {
  value = aws_eks_cluster.healthify.name
}

output "eks_cluster_endpoint" {
  value = aws_eks_cluster.healthify.endpoint
}

output "eks_cluster_security_group_id" {
  value = aws_eks_cluster.healthify.vpc_config[0].cluster_security_group_id
}

output "eks_node_security_group_id" {
  value = aws_security_group.eks_nodes.id
}
output "ecr_repository_urls" {
  value = {
    for name, repository in aws_ecr_repository.healthify :
    name => repository.repository_url
  }
}
output "rds_endpoint" {
  value = aws_db_instance.healthify.address
}

output "rds_port" {
  value = aws_db_instance.healthify.port
}

output "rds_database_name" {
  value = aws_db_instance.healthify.db_name
}
output "s3_bucket_name" {
  value = aws_s3_bucket.healthify_reports.bucket
}

output "s3_bucket_arn" {
  value = aws_s3_bucket.healthify_reports.arn
}