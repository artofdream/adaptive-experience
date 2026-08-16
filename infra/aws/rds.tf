resource "random_password" "db" {
  length  = 32
  special = false
}

resource "aws_db_subnet_group" "main" {
  name       = "${local.prefix}-db"
  subnet_ids = aws_subnet.private[*].id
  tags       = { Name = "${local.prefix}-db" }
}

resource "aws_db_instance" "main" {
  identifier                 = "${local.prefix}-postgres"
  engine                     = "postgres"
  engine_version             = "16"
  instance_class             = var.db_instance_class
  allocated_storage          = 50
  max_allocated_storage      = 200
  db_name                    = "adaptive_experience"
  username                   = "aea_app"
  password                   = random_password.db.result
  db_subnet_group_name       = aws_db_subnet_group.main.name
  vpc_security_group_ids     = [aws_security_group.rds.id]
  publicly_accessible        = false
  multi_az                   = false
  storage_encrypted          = true
  backup_retention_period    = 7
  deletion_protection        = false
  skip_final_snapshot        = true
  auto_minor_version_upgrade = true
  tags                       = { Name = "${local.prefix}-postgres" }
}
