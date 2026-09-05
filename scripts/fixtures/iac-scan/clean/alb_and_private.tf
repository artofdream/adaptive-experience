# Clean fixture for #334: public ALB may be world-open; non-ALB stays private.
variable "pilot_ingress_cidrs" {
  type        = list(string)
  description = "Public ALB CIDRs. Path B accepts 0.0.0.0/0."
  default     = ["0.0.0.0/0"]
}

resource "aws_security_group" "alb" {
  name        = "clean-alb"
  description = "Public ALB"
  vpc_id      = "vpc-12345678"

  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = var.pilot_ingress_cidrs
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_security_group" "rds" {
  name        = "clean-rds"
  description = "Postgres private"
  vpc_id      = "vpc-12345678"

  ingress {
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [aws_security_group.alb.id]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}
