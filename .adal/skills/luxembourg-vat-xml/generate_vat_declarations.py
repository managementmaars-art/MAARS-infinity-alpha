#!/usr/bin/env python3
"""
Generate Luxembourg quarterly VAT declarations (TVA_DECT) in eCDF XML format
"""

import xml.etree.ElementTree as ET
from xml.dom import minidom
from datetime import datetime
import csv
import json
import os
import sys

# Load configuration from vat_config.json
def load_config(config_path='vat_config.json'):
    """Load company configuration from JSON file"""
    if not os.path.exists(config_path):
        print(f"ERROR: Configuration file not found: {config_path}")
        print("Please copy vat_config.example.json to vat_config.json and fill in your details")
        sys.exit(1)
    
    with open(config_path, 'r') as f:
        return json.load(f)

# Default config (will be overridden by file)
CONFIG = {
    "company": {
        "MatrNbr": "YOUR_MATRICULE_NUMBER",
        "RCSNbr": "YOUR_RCS_NUMBER",
        "VATNbr": "YOUR_VAT_NUMBER",
        "eCDFPrefix": "YOUR_ECDF_PREFIX"
    },
    "vat_settings": {
        "usd_to_eur_rate": 0.923
    },
    "csv_file": "expenses.csv",
    "output_directory": "./output"
}

def parse_amount(amount_str):
    """Parse amount string to float"""
    if not amount_str or amount_str == "":
        return 0.0
    try:
        return float(str(amount_str).replace(',', '.').replace(' ', ''))
    except:
        return 0.0

def format_ecdf_number(value):
    """Format number with comma as decimal separator"""
    return f"{value:.2f}".replace('.', ',')

def calculate_quarter(quarter, config):
    """Calculate VAT fields for a specific quarter"""
    
    csv_file = config.get('csv_file', 'expenses.csv')
    providers = config.get('provider_categories', {})
    usd_to_eur = config.get('vat_settings', {}).get('usd_to_eur_rate', 0.923)
    
    # Check if CSV exists
    if not os.path.exists(csv_file):
        print(f"WARNING: CSV file not found: {csv_file}")
        print("Creating declaration with zero values")
        csv_file = None
    
    # Initialize counters
    field_458 = 0.0  # Luxembourg VAT (direct deduction)
    field_751 = 0.0  # Non-EU base at 17%
    field_752 = 0.0  # Non-EU VAT at 17%
    field_741 = 0.0  # EU base at 17%
    field_742 = 0.0  # EU VAT at 17%
    
    if csv_file:
        non_eu_providers = providers.get('non_eu_services', [])
        eu_providers = providers.get('eu_services', {})
        
        with open(csv_file, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row.get('Quarter') != quarter:
                    continue
                    
                provider = row.get('Provider', '')
                vat_rate = row.get('VAT Rate', '').replace('%', '')
                total = parse_amount(row.get('Total Amount (EUR)', '0'))
                currency = row.get('Currency', 'EUR')
                vat_amount = parse_amount(row.get('VAT Amount', '0'))
                notes = row.get('Notes', '')
                
                # Skip rent items (exempt)
                if 'Rent' in notes:
                    continue
                
                # Convert USD to EUR
                if currency == 'USD':
                    total = total * usd_to_eur
                
                # Categorize by provider type
                if provider in non_eu_providers:
                    # Non-EU services - reverse charge at 17%
                    base = total / 1.17
                    vat = base * 0.17
                    field_751 += base
                    field_752 += vat
                    
                elif provider in eu_providers:
                    # EU services - reverse charge at 17%
                    net_amount = parse_amount(row.get('Net Amount', '0'))
                    if net_amount > 0:
                        base = net_amount
                    else:
                        # Fallback: calculate from total
                        eu_vat_rate = eu_providers[provider].get('vat_rate', 0.20)
                        base = total / (1 + eu_vat_rate)
                    vat_lu = base * 0.17
                    field_741 += base
                    field_742 += vat_lu
                    
                else:
                    # Luxembourg suppliers - direct VAT deduction
                    if vat_amount > 0:
                        field_458 += vat_amount
    
    # Calculate derived fields (use rounded values to avoid validation errors)
    field_463 = field_751
    field_464 = field_752
    field_436 = field_741
    field_462 = field_742
    field_461 = field_464 + field_462
    field_409 = round(field_436, 2) + round(field_463, 2)
    field_410 = round(field_462, 2) + round(field_464, 2)
    field_093 = field_458 + field_461
    field_076 = field_410
    field_102 = field_093
    field_103 = field_076
    field_104 = field_102
    field_105 = field_103 - field_104
    
    return {
        '012': 0.0, '021': 0.0, '457': 0.0, '014': 0.0, '018': 0.0,
        '423': 0.0, '419': 0.0, '022': 0.0, '037': 0.0, '033': 0.0,
        '046': 0.0, '051': 0.0, '056': 0.0, '152': 0.0, '065': 0.0,
        '407': 0.0,
        '409': field_409,
        '436': field_436,
        '463': field_463,
        '765': 0.0,
        '410': field_410,
        '462': field_462,
        '464': field_464,
        '766': 0.0,
        '741': field_741,
        '742': field_742,
        '751': field_751,
        '752': field_752,
        '951': 0.0, '952': 0.0, '753': 0.0, '754': 0.0,
        '953': 0.0, '954': 0.0, '755': 0.0, '756': 0.0,
        '955': 0.0, '956': 0.0, '441': 0.0, '442': 0.0,
        '445': 0.0, '767': 0.0, '768': 0.0,
        '076': field_076,
        '458': field_458,
        '459': 0.0, '460': 0.0, '090': 0.0,
        '461': field_461,
        '092': 0.0, '228': 0.0,
        '093': field_093,
        '097': 0.0,
        '102': field_102,
        '103': field_103,
        '104': field_104,
        '105': field_105,
        '403': 0, '418': 0, '453': 0,
        '042': 0.0, '416': 0.0, '417': 0.0, '451': 0.0, '452': 0.0,
    }

def generate_xml(quarter, config, year=2024):
    """Generate eCDF XML for a specific quarter"""
    
    company = config['company']
    output_dir = config.get('output_directory', './output')
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    fields = calculate_quarter(quarter, config)
    period = {'Q1': 1, 'Q2': 2, 'Q3': 3, 'Q4': 4}[quarter]
    
    now = datetime.now()
    timestamp = now.strftime("%Y%m%dT%H%M%S")
    
    root = ET.Element("eCDFDeclarations")
    root.set("xmlns", "http://www.ctie.etat.lu/2011/ecdf")
    
    fileref = ET.SubElement(root, "FileReference")
    fileref.text = f"{company['eCDFPrefix']}{timestamp}{period:02d}"
    
    ET.SubElement(root, "eCDFFileVersion").text = "2.0"
    ET.SubElement(root, "Interface").text = "MODL5"
    
    agent = ET.SubElement(root, "Agent")
    ET.SubElement(agent, "MatrNbr").text = company["MatrNbr"]
    ET.SubElement(agent, "RCSNbr").text = company["RCSNbr"]
    ET.SubElement(agent, "VATNbr").text = company["VATNbr"]
    
    declarations = ET.SubElement(root, "Declarations")
    declarer = ET.SubElement(declarations, "Declarer")
    ET.SubElement(declarer, "MatrNbr").text = company["MatrNbr"]
    ET.SubElement(declarer, "RCSNbr").text = company["RCSNbr"]
    ET.SubElement(declarer, "VATNbr").text = company["VATNbr"]
    
    declaration = ET.SubElement(declarer, "Declaration")
    declaration.set("type", "TVA_DECT")
    declaration.set("model", "1")
    declaration.set("language", "FR")
    
    ET.SubElement(declaration, "Year").text = str(year)
    ET.SubElement(declaration, "Period").text = str(period)
    
    formdata = ET.SubElement(declaration, "FormData")
    
    first_batch_ids = ['012', '021', '457', '014', '018', '423', '419', '022', '037', 
                       '033', '046', '051', '056', '152', '065', '407', '409', '436', 
                       '463', '765', '410', '462', '464', '766', '741', '742', '751', 
                       '752', '951', '952', '753', '754', '953', '954', '755', '756', 
                       '955', '956', '441', '442', '445', '767', '768', '076', '458', 
                       '459', '460', '090', '461', '092', '228', '093', '097', '102', 
                       '103', '104', '105']
    
    for field_id in first_batch_ids:
        value = fields.get(field_id, 0.0)
        nf = ET.SubElement(formdata, "NumericField")
        nf.set("id", field_id)
        nf.text = format_ecdf_number(value)
    
    choices = {'204': 1, '205': 0}
    for choice_id, value in choices.items():
        choice = ET.SubElement(formdata, "Choice")
        choice.set("id", choice_id)
        choice.text = str(value)
    
    end_fields = {'403': 0, '418': 0, '453': 0}
    for field_id, value in end_fields.items():
        nf = ET.SubElement(formdata, "NumericField")
        nf.set("id", field_id)
        nf.text = str(value)
    
    final_batch_ids = ['042', '416', '417', '451', '452']
    for field_id in final_batch_ids:
        value = fields.get(field_id, 0.0)
        nf = ET.SubElement(formdata, "NumericField")
        nf.set("id", field_id)
        nf.text = format_ecdf_number(value)
    
    rough_string = ET.tostring(root, encoding='unicode')
    reparsed = minidom.parseString(rough_string)
    xml_str = reparsed.toprettyxml(indent="    ", encoding="UTF-8").decode('utf-8')
    
    lines = [line for line in xml_str.split('\n') if line.strip()]
    xml_str = '\n'.join(lines)
    
    filename = f"{company['eCDFPrefix']}{timestamp}{period:02d}.xml"
    filepath = os.path.join(output_dir, filename)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(xml_str)
    
    return filename, fields

def print_summary(quarter, fields):
    """Print summary of calculated fields"""
    print(f"\n{'='*60}")
    print(f"  {quarter} 2024 VAT DECLARATION SUMMARY")
    print(f"{'='*60}")
    print(f"  Field 458 (Luxembourg VAT):        {fields.get('458', 0):>10.2f} EUR")
    print(f"  Field 751 (Non-EU base 17%):       {fields.get('751', 0):>10.2f} EUR")
    print(f"  Field 752 (Non-EU VAT 17%):        {fields.get('752', 0):>10.2f} EUR")
    print(f"  Field 741 (EU base 17%):           {fields.get('741', 0):>10.2f} EUR")
    print(f"  Field 742 (EU VAT 17%):            {fields.get('742', 0):>10.2f} EUR")
    print(f"  {'─'*50}")
    print(f"  Field 463 (Total non-EU base):     {fields.get('463', 0):>10.2f} EUR")
    print(f"  Field 464 (Total non-EU VAT):      {fields.get('464', 0):>10.2f} EUR")
    print(f"  Field 461 (Deductible reverse):    {fields.get('461', 0):>10.2f} EUR")
    print(f"  {'─'*50}")
    print(f"  Field 093 (Total input VAT):       {fields.get('093', 0):>10.2f} EUR")
    print(f"  Field 105 (VAT credit/refund):     {fields.get('105', 0):>10.2f} EUR")
    print(f"{'='*60}")

if __name__ == "__main__":
    # Load configuration
    config = load_config()
    company_name = config.get('company', {}).get('name', 'Your Company')
    
    print("\n" + "="*60)
    print(f"  GENERATING 2024 QUARTERLY VAT DECLARATIONS")
    print(f"  {company_name}")
    print("="*60)
    
    for quarter in ['Q1', 'Q2', 'Q3', 'Q4']:
        filename, fields = generate_xml(quarter, config)
        print_summary(quarter, fields)
        print(f"  Generated: {filename}")
    
    print("\n" + "="*60)
    print("  ALL 4 QUARTERLY DECLARATIONS GENERATED")
    print("="*60)
