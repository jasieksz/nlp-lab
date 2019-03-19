import re

def register() -> str:
    base = r'W ustawie z dnia \d{1,2} \w* \d{4} r\.'
    title = r'((\w| )*)'
    ref = r'([\s\S]*?)(?=\))'
    return base + title + ref

def section() -> str:
    return r'\bArt\. \d*\.\n'

def journal() -> str:
    return r'Dz\.\s*(U|u)\. z \d{4} r\. Nr (\d*)\, poz\. (\d*)'

def date_title() -> str:
    return r'USTAWA\n\s*z dnia (\d{1,2}) (\w*) (\d{4}) r\.\s*((\w| |\n|\.)*?)(?=Art)'

def external_reference() -> str:
    return r'Dz\.\s*(U|u)\.([\s\S]*?)(?=\))'

def external_reference_ketless() -> str:
    return r'Dz\.\s*(U|u)\.([\s\S]*)(?=poz\. \d+\.)poz\. \d+\.'