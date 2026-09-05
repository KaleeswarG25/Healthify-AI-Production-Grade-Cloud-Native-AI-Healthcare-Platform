resource "aws_iam_role" "eks_cluster" {
  name = "${var.project_name}-eks-cluster-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"

    Statement = [
      {
        Effect = "Allow"

        Principal = {
          Service = "eks.amazonaws.com"
        }

        Action = "sts:AssumeRole"
      }
    ]
  })

  tags = {
    Name = "${var.project_name}-eks-cluster-role"
  }
}

resource "aws_iam_role_policy_attachment" "eks_cluster_policy" {
  role       = aws_iam_role.eks_cluster.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonEKSClusterPolicy"
}


resource "aws_eks_cluster" "healthify" {
  name     = var.project_name
  role_arn = aws_iam_role.eks_cluster.arn
  version  = var.eks_version

  vpc_config {
    subnet_ids = aws_subnet.private[*].id

    endpoint_private_access = true
    endpoint_public_access  = true
  }

  access_config {
    authentication_mode                         = "API_AND_CONFIG_MAP"
    bootstrap_cluster_creator_admin_permissions = true
  }

  depends_on = [
    aws_iam_role_policy_attachment.eks_cluster_policy
  ]

  tags = {
    Name = "${var.project_name}-eks"
  }
}


resource "aws_security_group" "eks_nodes" {
  name        = "${var.project_name}-eks-nodes-sg"
  description = "Security group for Healthify EKS worker nodes"
  vpc_id      = aws_vpc.healthify.id

  tags = {
    Name = "${var.project_name}-eks-nodes-sg"
  }
}


resource "aws_vpc_security_group_ingress_rule" "eks_nodes_self" {
  security_group_id = aws_security_group.eks_nodes.id

  description = "Allow node-to-node communication"

  ip_protocol = "-1"

  referenced_security_group_id = aws_security_group.eks_nodes.id
}


resource "aws_vpc_security_group_egress_rule" "eks_nodes_all" {
  security_group_id = aws_security_group.eks_nodes.id

  description = "Allow worker nodes outbound traffic"

  ip_protocol = "-1"

  cidr_ipv4 = "0.0.0.0/0"
}


resource "aws_iam_role" "eks_node" {
  name = "${var.project_name}-eks-node-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"

    Statement = [
      {
        Effect = "Allow"

        Principal = {
          Service = "ec2.amazonaws.com"
        }

        Action = "sts:AssumeRole"
      }
    ]
  })

  tags = {
    Name = "${var.project_name}-eks-node-role"
  }
}


resource "aws_iam_role_policy_attachment" "eks_worker_node_policy" {
  role       = aws_iam_role.eks_node.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonEKSWorkerNodePolicy"
}


resource "aws_iam_role_policy_attachment" "eks_cni_policy" {
  role       = aws_iam_role.eks_node.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonEKS_CNI_Policy"
}


resource "aws_iam_role_policy_attachment" "eks_ecr_readonly" {
  role       = aws_iam_role.eks_node.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryReadOnly"
}


resource "aws_eks_node_group" "general" {
  cluster_name = aws_eks_cluster.healthify.name

  node_group_name = "${var.project_name}-general"

  node_role_arn = aws_iam_role.eks_node.arn

  subnet_ids = aws_subnet.private[*].id

  instance_types = var.general_instance_types

  capacity_type = "ON_DEMAND"

  ami_type = "AL2023_x86_64_STANDARD"

  scaling_config {
    desired_size = var.general_desired_size
    min_size     = var.general_min_size
    max_size     = var.general_max_size
  }

  update_config {
    max_unavailable = 1
  }

  labels = {
    workload = "general"
  }

  depends_on = [
    aws_iam_role_policy_attachment.eks_worker_node_policy,
    aws_iam_role_policy_attachment.eks_cni_policy,
    aws_iam_role_policy_attachment.eks_ecr_readonly
  ]

  tags = {
    Name = "${var.project_name}-general-node-group"
  }
}


resource "aws_eks_node_group" "gpu" {
  cluster_name = aws_eks_cluster.healthify.name

  node_group_name = "${var.project_name}-gpu"

  node_role_arn = aws_iam_role.eks_node.arn

  subnet_ids = aws_subnet.private[*].id

  instance_types = var.gpu_instance_types

  capacity_type = "ON_DEMAND"

  ami_type = "AL2023_x86_64_NVIDIA"

  scaling_config {
    desired_size = var.gpu_desired_size
    min_size     = var.gpu_min_size
    max_size     = var.gpu_max_size
  }

  update_config {
    max_unavailable = 1
  }

  labels = {
    workload = "gpu"
  }

  taint {
    key    = "nvidia.com/gpu"
    value  = "true"
    effect = "NO_SCHEDULE"
  }

  depends_on = [
    aws_iam_role_policy_attachment.eks_worker_node_policy,
    aws_iam_role_policy_attachment.eks_cni_policy,
    aws_iam_role_policy_attachment.eks_ecr_readonly
  ]

  tags = {
    Name = "${var.project_name}-gpu-node-group"
  }
}