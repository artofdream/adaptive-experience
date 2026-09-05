# Known-bad fixture for #334: world-open ingress on a non-ALB security group.
resource "aws_security_group" "rds" {
  name        = "known-bad-rds"
  description = "World-open non-ALB fixture"
  vpc_id      = "vpc-12345678"

  ingress {
    from_port   = 5432
    to_port     = 5432
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
}
