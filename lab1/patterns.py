import re
from typing import List

def journal() -> str:
    return r'Dz\.\s*(U|u)\. z \d{4} r\. Nr (\d*)\, poz\. (\d*)'

def date_title() -> str:
    return r'USTAWA\n\s*z dnia (\d{1,2}) (\w*) (\d{4}) r\.\s*((\w| |\n|\.)*?)(?=Art)'
        
def register() -> str:
    base = r'W ustawie z dnia \d{1,2} \w* \d{4} r\.'
    title = r'((\w| )*)'
    ref = r'([\s\S]*?)(?=\))'
    return base + title + ref

def section() -> str:
    return r'\bArt\. \d*\.\n'

def paragraph() -> str:
    return r'\d+\.\s(?=[A-Z])'

def point() -> str:
    return r'\b\d+\)\s'

def external_reference() -> str:
    return r'Dz\.\s*(U|u)\.([\s\S]*?)(?=\))'

def external_reference_ketless() -> str:
    return r'Dz\.\s*(U|u)\.([\s\S]*)(?=poz\. \d+\.)poz\. \d+\.'
        
def internal_section_paragraph_point() -> str:
    s = r'\bart[\s\S]*?(?=\d+)(\d+)'
    p = r'[\s\S]*?(?=ust)ust[\s\S]*?(?=\d+)(\d+)'
    pt = r'[\s\S]*?(?=pkt)pkt[\s\S]*?(?=\d+)(\d+)'
    return s+p+pt
        
def internal_section_point() -> str:
    return r'\bart[\s\S]*?(?=\d+)(\d+)[\s\S]*?pkt[\s\S]*?(?=\d+)(\d+)'

def internal_section_paragraph() -> str:
    return r'\bart[\s\S]*?(?=\d+)(\d+)[\s\S]*?ust[\s\S]*?(?=\d+)(\d+)'

def internal_paragraph() -> str:
    return r'\bust. (\d+)'

def internal_pattern_order() -> List[str]:
    return [internal_section_paragraph_point(),
         internal_section_point(),
         internal_section_paragraph(),
         internal_paragraph()]