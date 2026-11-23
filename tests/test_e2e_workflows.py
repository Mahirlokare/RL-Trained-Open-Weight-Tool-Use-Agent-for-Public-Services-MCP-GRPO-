"""
End-to-End integration tests for multi-turn citizen service workflows.
"""
import pytest
from mcp_servers.services import create_default_mcp_hub
from agent.runtime import MCPAgentRuntime
from agent.reasoner import dynamic_rl_agent_policy

@pytest.fixture
def agent_runtime():
    hub = create_default_mcp_hub()
    return MCPAgentRuntime(mcp_hub=hub, model_fn=dynamic_rl_agent_policy, max_iterations=6)

def test_e2e_conversational_greeting(agent_runtime):
    traj = agent_runtime.run_task("greeting-test", "Hello! Who are you?")
    assert traj.success is True
    assert "Namaste" in traj.final_answer
    assert "Civic AI" in traj.final_answer

def test_e2e_scheme_search_workflow(agent_runtime):
    traj = agent_runtime.run_task("scheme-inquiry", "What hospitalization coverage does Ayushman Bharat PM-JAY provide?")
    assert traj.success is True
    assert "Ayushman Bharat" in traj.final_answer
    assert "500,000" in traj.final_answer or "5 Lakh" in traj.final_answer

def test_e2e_farmer_appointment_and_sms(agent_runtime):
    query = "Book an appointment for Devidas (PM_KISAN) at SEVA_NAGPUR_EAST and dispatch an SMS confirmation to his phone 9822334455."
    traj = agent_runtime.run_task("farmer-booking", query)
    assert traj.success is True
    assert "Appointment Confirmed" in traj.final_answer
    
    tools_called = [t.tool_call.name for t in traj.turns if t.tool_call]
    assert "check_center_slots" in tools_called
    assert "book_appointment" in tools_called
    assert "send_confirmation_sms" in tools_called

def test_e2e_senior_care_eligibility_disqualification(agent_runtime):
    query = "Check if a 70-year old senior citizen earning 500,000 INR annually qualifies for VAYO_SHRESTHA."
    traj = agent_runtime.run_task("senior-eligibility", query)
    assert traj.success is True
    assert "DOES NOT QUALIFY" in traj.final_answer or "not eligible" in traj.final_answer.lower()
