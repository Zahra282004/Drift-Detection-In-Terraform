terraform {
  backend "s3" {
    bucket = "my-tf-bucket-2004"
    key    = "terraform_state_file.tf"
    region = "us-east-1"
  }
}
