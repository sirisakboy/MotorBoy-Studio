"""
ECU State definitions - extended from eculib.honda.ECUSTATE
This module provides a function to get a patched ECUSTATE with SECURE state.
"""

from eculib.honda import ECUSTATE as BaseECUSTATE
from enum import Enum


def get_ecustate_with_secure():
    """
    Returns an ECUSTATE enum that includes the SECURE state.
    Since enums cannot be extended, we create a new enum with all values.
    """
    members = {e.name: e.value for e in BaseECUSTATE}
    members['SECURE'] = 100  # Add SECURE state
    
    class ExtendedECUSTATE(Enum):
        pass
    
    for name, value in members.items():
        setattr(ExtendedECUSTATE, name, value)
    
    return ExtendedECUSTATE


# Get the extended ECUSTATE
ECUSTATE = get_ecustate_with_secure()

# Also patch the eculib.honda module
import eculib.honda
eculib.honda.ECUSTATE = ECUSTATE

__all__ = ['ECUSTATE', 'get_ecustate_with_secure']