# 🏠 Smart Home Multi-Agent AI Coordinator

An autonomous, multi-agent AI system that monitors IoT device telemetry, diagnoses hardware/network anomalies, dispatches corrective commands, and intelligently escalates failures to human technicians.

## 🚀 Features
- **Multi-Agent Architecture**: Separation of concerns using specialized agents (Monitor, Diagnostics, Command, Escalation).
- **Strict JSON Enforcement**: Custom parsing logic ensures reliable state-passing between LLM agents without conversational hallucinations.
- **Automated Fallback Loop**: If an automated command fails (e.g., network timeout), the system automatically triggers an Escalation Agent to alert human operators.
- **Interactive Web UI**: A real-time Streamlit dashboard to trigger diagnostics and view agent execution logs and JSON outputs.

## 🛠️ Tech Stack
- **Language**: Python 3.12+
- **AI Framework**: [Strands Agents SDK](https://github.com/strands-agents/sdk-python) (powered by AWS Bedrock / Claude)
- **Frontend**: Streamlit
- **Tooling**: `boto3`, `python-dotenv`, `re`, `json`

## 🏗️ Architecture
```text
[Device ID Input] 
       │
       ▼
[1. Monitor Agent] ───(calls read_sensor_data)───▶ [Raw Sensor Data JSON]
       │
       ▼
[2. Diagnostics Agent] ─(calls diagnose_issue)───▶ [List of Issues JSON]
       │
       ▼
[3. Command Agent] ───(calls send_device_command)─▶ [Action Dispatched]
       │
       ├─✅ Success ──▶ [Pipeline Complete]
       │
       └─❌ Failure ──▶ [4. Escalation Agent] ──(calls send_alert_to_human)──▶ [Human Alert JSON]
