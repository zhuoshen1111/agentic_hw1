"""
test_hw1.py

The specification, as tests. Read it. Do not edit it.
These tests grade your work.
"""

import pytest
import inspect
from registrar import reset_registrar, enrolled_section_ids

try:
    from registrar_agent import agent, check_availability, enroll_student
except ImportError:
    agent = None
    check_availability = None
    enroll_student = None


def test_01_agent_has_tools():
    assert agent is not None, "TODO 1: define the Agent"
    assert len(agent.tools) >= 2, "Agent should have at least 2 tools"
    tool_names = [t.name if hasattr(t, "name") else t.__name__ for t in agent.tools]
    assert "check_availability" in tool_names, "TODO 1: add check_availability to Agent tools"
    assert "enroll_student" in tool_names, "TODO 1: add enroll_student to Agent tools"


def test_02_check_availability_schema():
    assert check_availability is not None, "TODO 2: implement check_availability"
    assert hasattr(check_availability, "__wrapped__"), "TODO 2: Use @function_tool"
    # Ensure docstring exists
    assert check_availability.__wrapped__.__doc__, "TODO 2: Add a docstring"
    

def test_03_enroll_student_idempotency():
    assert enroll_student is not None, "TODO 3: implement enroll_student"
    assert hasattr(enroll_student, "__wrapped__"), "TODO 3: Use @function_tool"
    
    reset_registrar()
    # First call
    res1 = enroll_student.__wrapped__("30412")
    assert "enrolled" in res1.lower()
    
    # Second call
    res2 = enroll_student.__wrapped__("30412")
    assert "already enrolled" in res2.lower()
    
    assert enrolled_section_ids().count("30412") == 1


def test_04_pytest_written(pytestconfig):
    # This just ensures the student actually wrote something in test_agent.py
    import test_agent
    funcs = [f for f in dir(test_agent) if f.startswith("test_")]
    assert len(funcs) >= 2, "TODO 5: Write at least two pytest functions in test_agent.py"

