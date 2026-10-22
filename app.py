import streamlit as st
import sys
import io

# Import the pipeline and agents from your backend file
from smart_home_device_mgmt import run_device_pipeline

st.set_page_config(page_title="Smart Home AI Coordinator", layout="wide")

st.title("🏠 Smart Home Multi-Agent Coordinator")
st.markdown("An autonomous AI pipeline that monitors, diagnoses, fixes, and escalates IoT device issues.")

# Sidebar for inputs
st.sidebar.header("Device Control Panel")
device_id = st.sidebar.text_input("Enter Device ID", value="dev_002")
run_button = st.sidebar.button("🚀 Run Diagnostic Pipeline", type="primary")

if run_button:
    with st.spinner(f"Running autonomous pipeline for {device_id}..."):
        
        # Capture terminal print statements to show in the UI
        captured_output = io.StringIO()
        sys.stdout = captured_output
        
        # Run the backend pipeline
        results = run_device_pipeline(device_id)
        
        # Reset stdout back to normal
        sys.stdout = sys.__stdout__
        
        # Display the agent logs
        st.subheader("📜 Agent Execution Logs")
        st.code(captured_output.getvalue(), language="text")
        
        # Display the final JSON results
        if results:
            st.subheader("🛠️ Dispatched Actions & Escalations")
            for res in results:
                issue_name = res.get('issue', 'Unknown').upper()
                with st.expander(f"Issue: {issue_name}"):
                    st.json(res)
        else:
            st.success("✅ No issues detected! Device is healthy.")
