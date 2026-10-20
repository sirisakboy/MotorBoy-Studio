import os, sys
import pytest
root = os.path.join(os.path.dirname(__file__), "..")
sys.path[:0] = [os.path.join(root, "src"), os.path.join(root, "Hart-ECU")]
pytest.importorskip("eculib.honda")  # needs pylibftdi / libftdi

def test_extended_ecustate_is_real_enum():
    from ecustate import ECUSTATE
    assert ECUSTATE.SECURE.value == 100
    assert ECUSTATE.OFF is ECUSTATE["OFF"]
    assert ECUSTATE.OFF != ECUSTATE.UNKNOWN

def test_eculib_patched():
    import eculib.honda
    from ecustate import ECUSTATE
    assert eculib.honda.ECUSTATE is ECUSTATE
