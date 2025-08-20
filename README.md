HoneyNet Cyber Defense — Smart Honeypots & AI Analysis
======================================================

[![Releases](https://img.shields.io/badge/Releases-Download-blue?logo=github)](https://github.com/Abdnour8/HoneyNet-CyberDefense/releases)

https://github.com/Abdnour8/HoneyNet-CyberDefense/releases

Hero image
![Network Defense](https://images.unsplash.com/photo-1555066931-4365d14bab8c?q=80&w=1200&auto=format&fit=crop&ixlib=rb-4.0.3&s=5f5f8e11a97f3a8f3bd8739288f7e8a6)

Table of contents
- Overview
- Key features
- Architecture
- Components
- Deployment
  - Docker Compose
  - FastAPI service
  - Quickstart (local)
- Honeypot recipes
- AI Threat Analysis
  - Model pipeline
  - Indicators and outputs
- Detection & response
- Integration and telemetry
- Configuration
- Security and hardening
- Releases
- Contributing
- License

Overview
--------
HoneyNet-CyberDefense combines smart honeypots, network sensors, and AI-driven analysis into a single platform. It captures attacker behavior, extracts indicators of compromise, and classifies threats with machine learning. The project targets defenders, SOC teams, and researchers who need realistic decoys, automated analysis, and scale.

Key features
------------
- Smart honeypots for common protocols: SSH, HTTP, SMB, MQTT, and custom TCP traps.
- Container-first design using Docker and Docker Compose.
- FastAPI control plane and API for orchestration and telemetry.
- AI threat analysis: behavior clustering, malware family classification, anomaly scoring.
- Automated artifacts: PCAPs, memory dumps, process traces.
- Detection rules export (Suricata, Zeek, Snort) and integration with SIEMs.
- Modular machine-learning pipeline for retraining on labeled events.
- Web UI and API for alerts, timeline view, and threat reports.
- Open-source, extensible Python code base.

Architecture
------------
![Architecture Diagram](https://upload.wikimedia.org/wikipedia/commons/3/3d/Network_security_diagram.svg)

- Sensors: Lightweight agents capture network traffic and logs.
- Honeypot layer: Protocol emulators and interactive decoys.
- Collector: Aggregates events, preserves artifacts, and stores in object storage.
- Analyzer (AI module): Runs feature extraction, model inference, and generates classification.
- Core API (FastAPI): Presents telemetry, controls honeypots, and manages deployments.
- Orchestration: Docker Compose or Kubernetes for production scale.
- Alerting: Webhooks, email, Slack, and SIEM connectors.

Components
----------
- fastapi-core: API and control plane.
- honeypot-templates: Protocol handlers and decoy scripts.
- sensor-agent: Packet capture and log forwarder.
- analyzer: ML models, feature store, and inference service.
- collector: Artifact storage, rotation, and retention policies.
- ui: Dashboard for timeline, evidence, and model feedback.

Deployment
----------
The project targets both local labs and production clusters. Use Docker Compose for quick setups. Use Kubernetes for larger deployments.

Docker Compose
- The repo includes docker-compose.yml to start core services:
  - api (FastAPI)
  - analyzer (ML inference)
  - collector (object store + DB)
  - honeypot instances (containerized templates)
- Common commands:
```bash
git clone https://github.com/Abdnour8/HoneyNet-CyberDefense.git
cd HoneyNet-CyberDefense
docker compose up -d
```

FastAPI service
- FastAPI exposes:
  - /api/v1/honeypots — list and control honeypots
  - /api/v1/events — event stream and filters
  - /api/v1/models — model metadata and retrain triggers
- Use /docs for interactive API docs when service runs.

Quickstart (local)
1. Clone repository and start default stack:
```bash
git clone https://github.com/Abdnour8/HoneyNet-CyberDefense.git
cd HoneyNet-CyberDefense
docker compose up -d
```
2. Open the dashboard:
- Default: http://localhost:8080
3. Start a basic SSH honeypot:
```bash
curl -X POST http://localhost:8080/api/v1/honeypots \
  -H "Content-Type: application/json" \
  -d '{"template":"ssh-basic","bind":"0.0.0.0:2222"}'
```
4. View events and artifacts at the UI or via API.

Honeypot recipes
---------------
The platform ships a set of honeypot templates. Each template includes an emulation layer and a capture policy.

- ssh-basic
  - Emulates an OpenSSH banner and offers a fake filesystem.
  - Captures commands, sessions, and binary uploads.
- http-interact
  - Serves dynamic pages, traps common scanners, and instruments requests for JS payload capture.
- mqtt-broker
  - Presents topics that lure IoT malware and records subscription and publish patterns.
- smb-decept
  - Emulates SMB file shares and logs file enumeration and SMB commands.
- tcp-raw
  - Generic TCP listener for unknown protocols; logs raw byte streams.

Customize templates:
- Templates live in /honeypot-templates.
- Add pre/post hooks to run scripts on event capture.
- Enable activity emulation with realistic timings and fake user data.

AI Threat Analysis
------------------
The analyzer processes raw events and produces structured outputs. The pipeline follows three stages: feature extraction, inference, and report generation.

Model pipeline
- Feature extraction
  - Extract behavioral features: sequence of commands, bytes patterns, timing, and network flows.
  - Produce feature vectors for each session or file.
- Inference
  - Ensemble models: behavior clustering + supervised classifiers.
  - Models include: Random Forest, LightGBM, and small Transformer-based sequence classifier for command traces.
- Feedback loop
  - Analysts can label events from the UI.
  - The retrain API picks up labeled examples and schedules retraining jobs.
- Storage
  - Store feature vectors and model metadata in a model store for versioning.

Indicators and outputs
- Event severity score (0-100).
- Malware family label (if classified).
- Behavioral cluster ID (for grouping similar attacks).
- IOC list: IPs, hashes, URLs, user agents.
- Recommended detection rules for Suricata and Zeek.

Example inference output:
```json
{
  "event_id": "evt-20250818-0001",
  "severity": 85,
  "malware_family": "ssh-brute-upload",
  "ioc": {
    "ip": "203.0.113.45",
    "sha256": "b6f4...88a9",
    "url": "http://mal.example/payload.bin"
  },
  "suricata_rule": "alert tcp any any -> $HOME_NET 22 (msg:\"HoneyNet SSH brute upload\"; sid:1000001; rev:1;)"
}
```

Detection & response
--------------------
- Built-in signatures export:
  - Generate Suricata and Zeek rules from high-confidence detections.
  - Use tags and thresholds to control rule generation.
- Alert pipelines:
  - Push alerts to Slack, email, or SIEM.
  - Integrate with SOAR platforms by calling webhooks or using the FastAPI control endpoints.
- Automated response:
  - Isolate source IPs with local firewall rules.
  - Sandbox uploaded binaries through analyzer and attach verdicts.

Integration and telemetry
-------------------------
- Exporters:
  - Prometheus metrics for health and telemetry.
  - Logs formatted for ELK or Graylog.
- Webhooks:
  - Custom webhook sink for alerts to third-party systems.
- APIs:
  - REST API for event queries.
  - WebSocket for live event streams.
- SIEM connectors:
  - Packets and events can forward to Splunk, Elastic, or QRadar.

Configuration
-------------
- config.yml controls global settings:
  - storage: object storage settings and rotation
  - retention: artifact retention policies
  - models: model store path and versions
  - api: bind address and auth
- Authentication:
  - API supports token-based auth and OAuth2.
  - Enable RBAC for team roles: analyst, operator, admin.
- Logging:
  - Configure log level and structured JSON output.
  - Forward logs to remote syslog or ELK.

Security and hardening
----------------------
- Run honeypots in isolated networks or VMs.
- Use dedicated object storage with lifecycle rules.
- Limit outbound connectivity from honeypot containers.
- Rotate API keys and use TLS for all control channels.
- Enable audit logging for all admin actions.

Releases
--------
Download and run the release files from the releases page:
https://github.com/Abdnour8/HoneyNet-CyberDefense/releases

The Releases page contains packaged binaries and installers. Download the appropriate release file for your platform and execute it to install the compiled components and deployment artifacts.

Sample commands (replace the filename with the chosen release asset):
```bash
# example placeholder commands; replace asset name with chosen release file
curl -L -o honeynet-release.tar.gz "https://github.com/Abdnour8/HoneyNet-CyberDefense/releases/download/vX.Y/honeynet-release.tar.gz"
tar -xzf honeynet-release.tar.gz
cd honeynet-release
chmod +x install.sh
sudo ./install.sh
```
If you use the GitHub UI, pick the asset that matches your OS or container runtime and follow the included install instructions.

Contributing
------------
- We accept pull requests and issues.
- Development workflow:
  - Fork the repo.
  - Create a branch for your feature or fix.
  - Add tests for logic and API changes.
  - Open a pull request with a clear description and linked issue.
- Labeling:
  - Use issue labels: bug, enhancement, docs, question.
- Tests:
  - Run unit tests with pytest:
```bash
pip install -r requirements-dev.txt
pytest
```
- Style:
  - Use black for formatting and flake8 for linting.

Support
-------
- Open issues to report bugs or request features.
- Use GitHub Discussions for design topics and deployment patterns.
- Provide reproducible logs and configuration snippets when reporting issues.

Project topics
--------------
This repo targets: ai-security, cyber-defense, cybersecurity, docker, fastapi, honeypot, intrusion-detection, machine-learning, malware-analysis, network-security, open-source, python, security-tools, threat-detection

Badges
------
[![Releases](https://img.shields.io/github/v/release/Abdnour8/HoneyNet-CyberDefense?label=Latest%20Release&logo=github)](https://github.com/Abdnour8/HoneyNet-CyberDefense/releases)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://www.python.org/)

License
-------
This project uses the Apache 2.0 license. See LICENSE file in the repository.

Images and assets
-----------------
- Use images under permissive licenses or use your own assets in /assets.
- Replace example images with project screenshots to document UI and workflows.

Contact
-------
Open an issue or discussion in the repository for technical questions, contributions, and integration requests.