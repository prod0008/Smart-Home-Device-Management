import os
import json
import re
from dotenv import load_dotenv
from strands import Agent

# Load AWS credentials from the .env file
load_dotenv()

# ==========================================
# 1. Mock Tools & Sample Data 
# (Replaces the Udacity starter file data)
# ==========================================
SAMPLE_DEVICES = {
    "dev_001": {"temperature": 72, "battery_level": 85, "network_latency_ms": 20},
    "dev_002": {"temperature": 105, "battery_level": 60, "network_latency_ms": 15}, # Will trigger overheating
    "dev_003": {"temperature": 68, "battery_level": 5, "network_latency_ms": 250}  # Will trigger low_battery & latency
}

def read_sensor_data(device_id: str) -> dict:
    """Retrieves sensor readings for a specific smart home device."""
    return SAMPLE_DEVICES.get(device_id, {"error": "Device not found"})

def diagnose_issue(sensor_data: dict) -> list:
    """Analyzes sensor data and returns a list of identified hardware or network issues."""
    issues = []
    if sensor_data.get("temperature", 0) > 90:
        issues.append("overheating")
    if sensor_data.get("battery_level", 100) < 10:
        issues.append("low_battery")
    if sensor_data.get("network_latency_ms", 0) > 200:
        issues.append("network_latency")
    return issues

def send_device_command(device_id: str, issue_type: str) -> dict:
    """Dispatches a corrective command to a device to resolve a specific issue."""
    actions = {
        "overheating": "activate_cooling_fan",
        "low_battery": "enable_power_saving_mode",
        "network_latency": "reboot_network_interface"
    }
    return {
        "device_id": device_id,
        "issue": issue_type,
        "command_sent": actions.get(issue_type, "no_action"),
        "status": "dispatched"
    }

# ==========================================
# 2. Helper for JSON Parsing
# ==========================================
def parse_agent_json(response_text):
    """Safely extracts and parses JSON from an LLM response, stripping markdown if present."""
    clean_text = re.sub(r'^```json\s*|\s*```$', '', response_text.strip(), flags=re.MULTILINE)
    try:
        return json.loads(clean_text)
    except json.JSONDecodeError:
        match = re.search(r'\{.*\}|\[.*\]', clean_text, re.DOTALL)
        if match:
            return json.loads(match.group(0))
        raise ValueError(f"Could not parse JSON from agent response: {response_text}")

# ==========================================
# 3. Build the Agents (TODOs 1, 2, 3)
# ==========================================
monitor_agent = Agent(
    system_prompt=(
        "You are the Device Monitor agent. Your sole purpose is to retrieve sensor data. "
        "Call the read_sensor_data tool with the provided device ID. "
        "You must output ONLY a valid JSON object containing the raw sensor data. "
        "Do not include any conversational text, greetings, or markdown formatting."
    ),
    tools=[read_sensor_data]
)

diagnostics_agent = Agent(
    system_prompt=(
        "You are the Diagnostics agent. Your sole purpose is to identify device anomalies. "
        "Call the diagnose_issue tool with the provided sensor data. "
        "You must output ONLY a valid JSON object with a single key 'issues' containing a list of issue types (strings). "
        "Example: {\"issues\": [\"overheating\", \"low_battery\"]}. "
        "Do not include any conversational text or markdown formatting."
    ),
    tools=[diagnose_issue]
)

command_agent = Agent(
    system_prompt=(
        "You are the Command agent. Your sole purpose is to dispatch corrective actions. "
        "Call the send_device_command tool with the provided device ID and issue type. "
        "You must output ONLY a valid JSON object confirming the action. "
        "Example: {\"device_id\": \"dev_123\", \"issue\": \"overheating\", \"command_sent\": \"cool_down\", \"status\": \"success\"}. "
        "Do not include any conversational text or markdown formatting."
    ),
    tools=[send_device_command]
)

# ==========================================
# 4. Wire the Coordinator (TODOs 4, 5, 6)
# ==========================================
def run_device_pipeline(device_id):
    print(f"\n{'='*20} Starting Pipeline for Device: {device_id} {'='*20}")
    
    # TODO 4: Execute the Device Monitor
    try:
        monitor_response = monitor_agent(f"Retrieve sensor data for device {device_id}")
        # Handle both string responses and Strands AgentResponse objects
        monitor_text = getattr(monitor_response, 'text', str(monitor_response))
        sensor_data = parse_agent_json(monitor_text)
        print(f"[Monitor] ✅ Retrieved data: {sensor_data}")
    except Exception as e:
        print(f"[Monitor] ❌ Error: Failed to get or parse sensor data. Details: {e}")
        return

    # TODO 5: Execute the Diagnostics agent
    try:
        prompt_data = json.dumps(sensor_data)
        diag_response = diagnostics_agent(f"Analyze the following sensor data for anomalies: {prompt_data}")
        diag_text = getattr(diag_response, 'text', str(diag_response))
        
        diag_result = parse_agent_json(diag_text)
        issues = diag_result.get("issues", [])
        print(f"[Diagnostics] ✅ Identified issues: {issues}")
    except Exception as e:
        print(f"[Diagnostics] ❌ Error: Failed to diagnose issues. Details: {e}")
        return

    # TODO 6: Execute the Command agent
    command_results = []
    if not issues:
        print("[Command] ℹ️ No issues found. Pipeline complete.")
        return command_results
        
    for issue in issues:
        try:
            cmd_response = command_agent(f"Dispatch corrective action for device {device_id} regarding issue: {issue}")
            cmd_text = getattr(cmd_response, 'text', str(cmd_response))
            
            cmd_result = parse_agent_json(cmd_text)
            command_results.append(cmd_result)
            print(f"[Command] ✅ Dispatched for '{issue}': {cmd_result}")
        except Exception as e:
            print(f"[Command] ❌ Error: Failed to dispatch command for '{issue}'. Details: {e}")
            
    return command_results

if __name__ == "__main__":
    # Test the pipeline against our 3 mock devices
    test_devices = ["dev_001", "dev_002", "dev_003"]
    for dev in test_devices:
        run_device_pipeline(dev)
