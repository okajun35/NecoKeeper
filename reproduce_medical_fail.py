import sys

import pytest

# We need to make sure we use the same conftest configuration
# But running pytest directly on the file is better.

if __name__ == "__main__":
    sys.exit(
        pytest.main(
            ["tests/test_medical_records.py", "-v", "-k", "test_get_medical_record_api"]
        )
    )
