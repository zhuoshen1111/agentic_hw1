"""
Phase 3: Trust but Verify

Test your tools in isolation using standard pytest.
Then test the Runner's control flow using a mock.
"""

import pytest
from registrar import (
    reset_registrar,
    enrolled_section_ids,
    STUDENT_ID,
    CATALOG_OBSERVED_AS_OF,
)
from registrar_agent import check_availability, enroll_student

def setup_function():
    reset_registrar()

# TODO 5: Test the tools in isolation
# Write a pytest function to verify `check_availability` returns the timestamp.
"""
Phase 3: Trust but Verify

Test your tools in isolation using standard pytest.
Then test the Runner's control flow using a mock.
"""

import pytest
from registrar import (
    reset_registrar,
    enrolled_section_ids,
    STUDENT_ID,
    CATALOG_OBSERVED_AS_OF,
)
from registrar_agent import check_availability, enroll_student


def setup_function():
    reset_registrar()


# TODO 5: Test the tools in isolation
# Write a pytest function to verify `check_availability` returns the timestamp.
def test_check_availability_returns_timestamp():
    result = check_availability.__wrapped__("30412")

    assert result["section_id"] == "30412"
    assert result["observed_as_of"] == CATALOG_OBSERVED_AS_OF


# Write a pytest function to verify `enroll_student` idempotency.
def test_enroll_student_is_idempotent():
    first_result = enroll_student.__wrapped__("30412")
    second_result = enroll_student.__wrapped__("30412")

    assert STUDENT_ID in first_result
    assert "enrolled" in first_result.lower()
    assert "already enrolled" in second_result.lower()
    assert enrolled_section_ids() == ["30412"]

