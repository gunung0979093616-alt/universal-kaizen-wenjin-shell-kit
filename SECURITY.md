# Security Policy

## Scope

This repository contains a portable command-execution and evidence toolkit. It is designed to reduce the risk of treating unverified model output as execution proof.

## Do not disclose secrets

Never include the following in issues, pull requests, commits, ZIP archives, or test fixtures:

- API keys or access tokens
- OAuth client secrets or refresh tokens
- Passwords
- Private keys or certificates containing private key material
- Database credentials
- Deployment credentials
- Customer or personal data

## Reporting a vulnerability

For a suspected security vulnerability, avoid publishing exploitable details in a public issue. Contact the repository maintainer privately through the contact method associated with the GitHub account that maintains this repository.

When reporting, include the affected file or command, reproduction steps that do not expose secrets, expected behavior, observed behavior, and potential impact.

## Security limitations

The Shell Gate is a safety-oriented command runner, not a complete sandbox or operating-system security boundary. Do not treat its command filters as a substitute for OS permissions, container isolation, CI security controls, or project-specific authorization.
