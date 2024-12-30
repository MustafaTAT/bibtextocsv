import sys
import os.path
import csv
import re

class Converter:
    def __init__(self):
        self.bibfile = ''
        self.attributes = set()
        self.datas = []

    def setBibfile(self, bibfile):
        self.bibfile = bibfile
        # Split file into entries
        entry_pattern = r'@(\w+)\s*{\s*([^,]*),\s*(.*?)\n}\s*(?=@|\Z)'
        entries = re.finditer(entry_pattern, self.bibfile, re.DOTALL)
        
        for entry_match in entries:
            entry_type = entry_match.group(1)
            entry_id = entry_match.group(2)
            entry_body = entry_match.group(3)
            
            attributes = self.extract_attributes(entry_body)
            self.attributes.update(attributes.keys())
            self.datas.append((entry_type.strip(), entry_id.strip(), attributes))

    def extract_attributes(self, entry_body):
        attributes = {}
        # Match attribute pattern: key = value
        attr_pattern = r'(\w+)\s*=\s*({[^}]*}|"[^"]*"|[^,\n]*),?'
        
        for match in re.finditer(attr_pattern, entry_body):
            key = match.group(1).strip()
            value = match.group(2).strip()
            
            # Clean up the value
            value = value.strip('{}"')  # Remove outer braces and quotes
            value = re.sub(r'\s+', ' ', value)  # Normalize whitespace
            
            if key and value:  # Only add non-empty attributes
                attributes[key] = value
                
        return attributes

    def generate(self, file):
        with open(file, "w", newline='', encoding='utf-8') as f2w:
            writer = csv.writer(f2w, delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            header = ['type', 'id'] + sorted(self.attributes)
            writer.writerow(header)
            for entry_type, entry_id, attributes in self.datas:
                row = [entry_type, entry_id] + [attributes.get(attr, '').replace(';', ',') for attr in sorted(self.attributes)]
                while len(row) < len(header):
                    row.append('')
                writer.writerow(row)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python bibtocvs.py input.bib output.csv")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]

    if os.path.exists(input_file):
        converter = Converter()
        with open(input_file, 'r', encoding='utf-8') as f:
            converter.setBibfile(f.read())
        converter.generate(output_file)
        print(f'Conversion complete: {input_file} to {output_file}')
    else:
        print(f"Error: File {input_file} does not exist.")
