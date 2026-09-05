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