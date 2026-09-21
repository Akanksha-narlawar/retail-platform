# Retail Platform

## Application
Online retail platform used for demonstrating Git, Jenkins and Docker deployment.

## Current Production Version
4.2.0

## Branches
- main - production-ready code
- develop - ongoing development
- release/4.3.0 - release preparation
- hotfix/payment-4.2.1 - emergency payment fix

## Docker
The application runs inside a Docker container.

Host Port: 8081
Container Port: 5000

## Health Check
The application provides:

/health

A healthy application returns HTTP 200.

## Version Traceability
Every production release is identified by a Git tag and Docker image version.

Example:

Git tag: v4.2.1
Docker image: retail-app:4.2.1