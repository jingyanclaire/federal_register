import re
import pandas as pd


def process_text(text):
    sections = ["Rules and Regulations", "Proposed Rules", "Notices"]
    current_section = None
    entries = []
    current_entry = {'Text': ''}
    agency_name = ''
    capture_agency_name = False
    current_department = None

    for line in text.split('\n'):
        line = line.strip()

        for section in sections:
            if section in line:
                if current_entry['Text'].strip():
                    current_entry['Length'] = len(current_entry['Text'].split())
                    entries.append(current_entry)
                current_section = section
                current_entry = {'Type': current_section, 'Text': ''}
                break

        if re.match(r'\[FR Doc. \d{2}–\d{5} Filed \d{2}–\d{2}–\d{2}; \d{1,2}:\d{2} am\]', line):
            current_entry['Date'] = re.search(r'\d{2}–\d{2}–\d{2}', line).group()
            current_entry['Length'] = len(current_entry['Text'].split())
            entries.append(current_entry)
            current_entry = {'Type': current_section, 'Text': ''}
            continue

        if current_entry['Text'] == '' and line.isupper() and re.match(r'^[A-Z\s]+$', line):
            current_department = line
            continue


        if "AGENCY:" in line:
            agency_name = line.split("AGENCY:", 1)[1].strip()
            continue

        if agency_name and "ACTION:" not in line:
            agency_name += ' ' + line
            continue

        if "ACTION:" in line:
            current_entry['Agency'] = agency_name.strip()
            current_entry['Department'] = current_department
            agency_name = ''
            continue

        current_entry['Text'] += ' ' + line

    df = pd.DataFrame(entries)
    return df


with open(r'D:\pycharm\pythonProject\pdf-txt\FR\FR-1990\01\1990-01-02.txt', 'r', encoding='utf-8') as file:
    text = file.read()

df = process_text(text)
print(df)
df.to_csv('output.csv')