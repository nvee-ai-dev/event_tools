"""
Tests for detritus.file_manager
This file complements test_main.py by adding more specific tests for FileManager.
"""

import sys
import os
from pathlib import Path
import event_tools.file_manager as fm

TEMP_TEST_DIR_FM = "data_fm_specific_tests"
TEST_JSON_FILE_FM = "test_fm.json"
TEST_DICT_FM = {"ding_fm": 1, "dong_fm": 2}
TEST_LIST_FM = [TEST_DICT_FM, {"ding_fm": 3, "dong_fm": 4}]


def setup_module(module):
    """Setup any state tied to the execution of the given module."""
    # Ensure the test directory is clean before starting tests in this module
    if Path(TEMP_TEST_DIR_FM).exists():
        fm.FileManager.delete_dir(TEMP_TEST_DIR_FM)
    Path(TEMP_TEST_DIR_FM).mkdir(parents=True, exist_ok=True)


def teardown_module(module):
    """Teardown any state that was previously setup with a setup_module
    call.
    """
    fm.FileManager.delete_dir(TEMP_TEST_DIR_FM)


def test_json_file_operations():
    fmgr = fm.FileManager(TEMP_TEST_DIR_FM, TEST_JSON_FILE_FM)
    assert not fmgr.exists()
    fmgr.dump(data=TEST_LIST_FM, indent=4)
    assert fmgr.exists()
    read_data = fmgr.load()
    assert read_data == TEST_LIST_FM
    fmgr.delete_file()
    assert not fmgr.exists()
    print("test_json_file_operations passed.")


# Pytest will discover and run test functions automatically.
# The main() function and if __name__ == "__main__": block are not needed for pytest.
# def main() -> int:
# if __name__ == "__main__":
#     sys.exit(main())
