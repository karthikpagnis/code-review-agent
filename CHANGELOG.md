# Changelog

All notable changes to Code Review Agent will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [1.0.0] - 2026-05-06

### Added
- Multi-agent code review system with three specialist agents:
  - Security agent (OWASP vulnerabilities, hardcoded secrets, injection attacks)
  - Logic/Bug agent (null references, exceptions, race conditions)
  - Quality agent (naming conventions, documentation, complexity)
- Azure Entra ID OAuth2 authentication via MSAL.js
- FastAPI REST API with JWT validation
- LangGraph-based orchestrator for parallel agent execution
- Azure AI Foundry integration with GPT-4o model
- Azure Blob Storage for report persistence
- Python AST-based code chunking
- Interactive HTML frontend with report table visualization
- Support for GitHub file URLs (public repos only)
- Direct code snippet submission
- Comprehensive setup guides (CLI and web portal)
- API documentation (Swagger/OpenAPI)

### Documentation
- Complete README with architecture diagram
- Step-by-step Azure setup guide (CLI method)
- Web portal setup guide (no CLI required)
- Deployment guide for Azure App Service
- API reference documentation
- Contributing guidelines
- Competition submission guide
- Troubleshooting section

### Infrastructure
- Azure resource group setup
- Entra ID app registration with OAuth2 scopes
- Azure AI Foundry project with GPT-4o deployment
- Azure Blob Storage with reports container
- Cost estimation and optimization

### Project Structure
```
code-review-agent/
├── app/
│   ├── main.py (FastAPI entry point)
│   ├── auth.py (JWT validation)
│   ├── agents/ (security, logic, quality, aggregator, orchestrator)
│   ├── routers/ (review endpoint)
│   ├── schemas/ (Pydantic models)
│   └── utils/ (GitHub fetcher, Blob storage)
├── frontend/
│   └── index.html (MSAL login + review form + report table)
├── infra/
│   ├── azure_setup.md (CLI setup)
│   └── azure_setup_web.md (Web portal setup)
├── DEPLOYMENT.md (Azure App Service deployment)
├── CONTRIBUTING.md (Contribution guidelines)
├── COMPETITION_SUBMISSION.md (Competition readiness guide)
├── LICENSE (MIT)
├── README.md
├── requirements.txt
└── .env.example
```

### Licenses & Dependencies
- MIT License
- Python 3.11+
- FastAPI + Uvicorn
- LangGraph for agent orchestration
- Azure AI Foundry Agent SDK
- MSAL.js for frontend authentication
- httpx for HTTP requests
- python-jose for JWT handling
- azure-storage-blob for report persistence
- pydantic for schema validation

---

## [Unreleased]

### Planned Features
- [ ] Support for more programming languages (JavaScript, Java, C++, Go)
- [ ] Docker containerization for easy deployment
- [ ] CI/CD pipeline (GitHub Actions)
- [ ] Unit tests and integration tests
- [ ] Performance improvements for large files
- [ ] Batch review API (multiple files at once)
- [ ] Custom rules engine for organizations
- [ ] Web UI improvements (real-time progress, downloadable reports)
- [ ] Slack/Teams integration for sharing reports
- [ ] GitHub integration for PR comments
- [ ] Historical report tracking and trend analysis
- [ ] Rate limiting and usage quotas
- [ ] Admin dashboard for monitoring

### Known Issues
- Large files (>500KB) may timeout on free tier
- GPT-4o model deployment takes 10-15 minutes
- Blob Storage connection string errors if container doesn't exist

### Performance Roadmap
- [ ] Implement caching for repeated code analysis
- [ ] Add model response streaming
- [ ] Optimize AST chunking for very large files
- [ ] Parallel blob uploads

---

## How to Report Issues

Found a bug? See [CONTRIBUTING.md](CONTRIBUTING.md#reporting-bugs)

---

## Credits

**Developed by:** Karthik Pagnis
**Built on:** Azure AI Foundry, LangGraph, FastAPI
**Year:** 2026
**Purpose:** Portfolio project / Competition submission

---

## License

This project is licensed under the MIT License - see [LICENSE](LICENSE) file for details.

---

## Version History

| Version | Date | Status |
|---------|------|--------|
| 1.0.0 | 2026-05-06 | ✅ Released |
| Future | TBD | 🔄 In Development |

---

## Acknowledgments

- Microsoft Azure team for student credits
- Azure AI Foundry documentation
- LangGraph framework
- FastAPI framework
- GitHub for hosting
