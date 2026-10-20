"""
ECU Data Database - Imported from PDF files
Contains Honda, Suzuki, KTM ECU models and fault codes
"""

import json
import os

# Load database
_db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'databases', 'ecu_data.json')
with open(_db_path, 'r', encoding='utf-8') as f:
    DATA = json.load(f)


def get_honda_models():
    """Get list of Honda ECU models"""
    return DATA['honda']['ecu_models']


def get_honda_dtc(code):
    """Get Honda DTC code description"""
    codes = DATA['honda']['dtc_codes']
    return codes.get(str(code))


def get_suzuki_models():
    """Get list of Suzuki ECU models"""
    return DATA['suzuki']['ecu_models']


def get_ktm_dtc(code):
    """Get KTM DTC code description"""
    for item in DATA['ktm']['dtc_codes']:
        if item['code'] == code:
            return item
    return None


def find_ecu_by_pn(part_number, brand='honda'):
    """Find ECU by part number"""
    if brand.lower() == 'honda':
        models = get_honda_models()
    elif brand.lower() == 'suzuki':
        models = get_suzuki_models()
    else:
        return None
    
    for model in models:
        if model.get('pn', '').upper() == part_number.upper():
            return model
    return None


def get_all_brands():
    """Get list of supported brands"""
    return list(DATA.keys())