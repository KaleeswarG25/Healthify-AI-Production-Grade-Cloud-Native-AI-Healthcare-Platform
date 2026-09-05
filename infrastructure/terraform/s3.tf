resource "aws_s3_bucket" "healthify_reports" {
  bucket = var.s3_bucket_name

  tags = {
    Name    = var.s3_bucket_name
    Service = "medical-reports"
  }
}


resource "aws_s3_bucket_public_access_block" "healthify_reports" {
  bucket = aws_s3_bucket.healthify_reports.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}


resource "aws_s3_bucket_versioning" "healthify_reports" {
  bucket = aws_s3_bucket.healthify_reports.id

  versioning_configuration {
    status = "Enabled"
  }
}


resource "aws_s3_bucket_server_side_encryption_configuration" "healthify_reports" {
  bucket = aws_s3_bucket.healthify_reports.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }

    bucket_key_enabled = true
  }
}


resource "aws_s3_bucket_lifecycle_configuration" "healthify_reports" {
  bucket = aws_s3_bucket.healthify_reports.id

  rule {
    id     = "abort-incomplete-multipart-uploads"
    status = "Enabled"

    filter {
      prefix = ""
    }

    abort_incomplete_multipart_upload {
      days_after_initiation = 7
    }
  }
}