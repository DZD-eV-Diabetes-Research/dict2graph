import os, sys

if __name__ == "__main__":
    SCRIPT_DIR = os.path.dirname(
        os.path.realpath(os.path.join(os.getcwd(), os.path.expanduser(__file__)))
    )
    MODULE_ROOT_DIR = os.path.join(SCRIPT_DIR, "..")
    sys.path.insert(0, os.path.normpath(MODULE_ROOT_DIR))
os.environ["DICT2GRAPH_RUN_ALL_TESTS"] = "true"
from dict2graph_tests import (
    test_basics,
    test_docs_cases,
    test_node_trans,
    test_rel_trans,
    test_integration_tests,
)
