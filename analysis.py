import re
import pandas as pd

with open(r'D:\pycharm\pythonProject\pdf-txt\FR\FR-1990\01\1990-01-02.txt', 'r', encoding='utf-8') as file:
    text = file.read()


separator_pattern = r'\[FR Doc\. \d{2}\–\d{5} Filed \d{2}–\d{2}–\d{2}; \d{1,2}:\d{2} am\]'


entries = re.split(separator_pattern, text)


date_pattern = r'Vol\.\s\d+,\sNo\.\s\d+\n.+\d{4}'
department_pattern = r'(DEPARTMENT OF [A-Z\s]+)'


matrix = []


for entry in entries:
    date_match = re.search(date_pattern, entry)
    department_match = re.search(department_pattern, entry)

    date = date_match.group().strip() if date_match else ''
    department_name = department_match.group(1).strip() if department_match else ''


    agency_name = ''
    if department_name:
        lines = entry.split('\n')
        for i, line in enumerate(lines):
            if line.strip() == department_name:
                for next_line in lines[i + 1:]:
                    if next_line.strip():
                        agency_name = next_line.strip()
                        break
                break

    entry_type = "Rule" if "Rules and Regulations" in entry else "Proposed Rule" if "Proposed Rules" in entry else "Notice"
    length_of_entry = len(entry.split())
    text_of_entry = entry.strip()

    matrix.append([date, entry_type, department_name, agency_name, length_of_entry, text_of_entry])


df = pd.DataFrame(matrix, columns=['Date', 'Type of entry', 'Department name', 'Agency name', 'Length of entry',
                                   'Text of entry'])


print(df)
df.to_csv('output.csv')