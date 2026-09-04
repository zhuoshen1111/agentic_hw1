"""
Phase 3: Trust but Verify

Test your tools in isolation using standard pytest.
Then test the Runner's control flow using a mock.
"""

import pytest
from registrar import reset_registrar, enrolled_section_ids, STUDENT_ID
from registrar_agent import check_availability, enroll_student

def setup_function():
    reset_registrar()

# TODO 5: Test the tools in isolation
# Write a pytest function to verify `check_availability` returns the timestamp.
raise NotImplementedError("TODO 5 -- see the comment above")

# Write a pytest function to verify `enroll_student` idempotency.
raise NotImplementedError("TODO 5 -- see the comment above")
