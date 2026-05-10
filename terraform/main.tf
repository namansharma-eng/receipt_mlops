terraform {
  required_providers {
    aws = { source = "hashicorp/aws", version = "~> 5.0" }
  }
}

provider "aws" {
  region = "ap-south-1"
}

variable "receipt-key" {
  description = "receipt-key"
}

data "aws_ami" "ubuntu" {
  most_recent = true
  owners      = ["099720109477"]
  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd/ubuntu-*-24.04-amd64-server-*"]
  }
}

resource "aws_security_group" "receipt_sg" {
  name = "receipt-mlops-sg"

  ingress { from_port = 22;   to_port = 22;   protocol = "tcp"; cidr_blocks = ["0.0.0.0/0"] }
  ingress { from_port = 8000; to_port = 8000; protocol = "tcp"; cidr_blocks = ["0.0.0.0/0"] }
  ingress { from_port = 3000; to_port = 3000; protocol = "tcp"; cidr_blocks = ["0.0.0.0/0"] }
  ingress { from_port = 9090; to_port = 9090; protocol = "tcp"; cidr_blocks = ["0.0.0.0/0"] }
  egress  { from_port = 0;    to_port = 0;    protocol = "-1";  cidr_blocks = ["0.0.0.0/0"] }
}

resource "aws_instance" "receipt_server" {
  ami                    = data.aws_ami.ubuntu.id
  instance_type          = "t3.micro"
  key_name               = var.receipt-key
  vpc_security_group_ids = [aws_security_group.receipt_sg.id]

  user_data = <<-EOF
    #!/bin/bash
    apt-get update -y
    apt-get install -y docker.io docker-compose-plugin git
    systemctl enable docker
    systemctl start docker
    usermod -aG docker ubuntu
    git clone https://github.com/namansharma-eng/receipt_mlops.git /home/ubuntu/receipt_mlops
    cd /home/ubuntu/receipt_mlops
    docker compose up -d
  EOF

  tags = { Name = "receipt-mlops" }
}

resource "aws_eip" "eip" {
  instance = aws_instance.receipt_server.id
  domain   = "vpc"
}

output "api_url"      { value = "http://${aws_eip.eip.public_ip}:8000" }
output "grafana_url"  { value = "http://${aws_eip.eip.public_ip}:3000" }
output "ssh_command"  { value = "ssh -i ~/.ssh/${var.receipt-key}.pem ubuntu@${aws_eip.eip.public_ip}" }