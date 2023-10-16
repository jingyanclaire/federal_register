import requests
import io
import os
import re
from concurrent.futures import ThreadPoolExecutor
import fitz

# RE = r'\s*F\s*e\s*d\s*e\s*r\s*a\s*l\s*R\s*e\s*g\s*i\s*s\s*t\s*e\s*r\s*/\s*V\s*o\s*l\s*'
RE = r'\s*F\s*[éèêëeE]\s*d\s*[éèêëeE]\s*r\s*a\s*l\s*R\s*[éèêëeE]\s*g\s*[LIil1íìîï]\s*s\s*t\s*[éèêëeE]\s*r\s*/\s*V\s*[Oo0óòôöõøœ]\s*[LIil1íìîï]\s*'



def fix_vowels_line(line):
    replacements = {
        'á': 'a', 'à': 'a', 'â': 'a', 'ä': 'a', 'ã': 'a', 'å': 'a', 'æ': 'a',
        'é': 'e', 'è': 'e', 'ê': 'e', 'ë': 'e',
        'í': 'i', 'ì': 'i', 'î': 'i', 'ï': 'i',
        'ó': 'o', 'ò': 'o', 'ô': 'o', 'ö': 'o', 'õ': 'o', 'ø': 'o',
        'ú': 'u', 'ù': 'u', 'û': 'u', 'ü': 'u',
        'ÿ': 'y', 'ý': 'y',
        'œ': 'o', 'ñ': 'n', 'ç': 'c'
    }
    for old, new in replacements.items():
        line = line.replace(old, new)
    if re.match(RE, line):
        line = re.sub(r'\s+', '', line)

    return line

def extract_text_from_page(page):
    blocks = page.get_text("blocks")
    blocks.sort(key=lambda x: -x[3])
    text = ""
    last_block = None
    for b in blocks:
        if last_block and abs(b[3] - last_block[3]) > 3:
            text += "\n"
        text += b[4].strip()
        last_block = b
    return text


def get_txt(date, pdf_stream, folder_path):
    print(f"Extracting text from PDF for date: {date}")
    pdf_document = fitz.open(stream=pdf_stream)
    lines = []
    for page_num in range(len(pdf_document)):
        page = pdf_document.load_page(page_num)
        text = extract_text_from_page(page)
        for line in text.split('\n'):
            if re.match(RE, line):
                line = fix_vowels_line(line)
            lines.append(line)

    with open(f'{folder_path}/{date}.txt', 'w', encoding='utf-8') as file:
        file.write('\n'.join(lines))

def make_folder(year, month, date, pdf_file):
    folder_path = f"D:\\pycharm\\pythonProject\\pdf-txt\\FR(miner)\\FR-{year}\\{month}"
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    get_txt(date, pdf_file, folder_path)


def process_date(date_list):
    year,month,day = date_list

    date = f"{year}-{month}-{day}"
    url = f"https://www.govinfo.gov/content/pkg/FR-{date}/pdf/FR-{date}.pdf"
    response = requests.get(url)
    if response.status_code == 200 and response.url == url:
        pdf_file = io.BytesIO(response.content)
        make_folder(year, month, date, pdf_file)
        pdf_file.close()
    response.close()


def find_empty():
    # need to change the path of Empytfile
    with open(r'D:\pycharm\pythonProject\pdf-txt\Emptyfile.txt', 'r', encoding='utf-8') as file:
        return file.readlines()


def main():
    li = find_empty()
    date_list = []
    for name in li:
        year = name[:4]
        month = name[5:7]
        day = name[8:10]
        date_list.append((year, month, day))

    with ThreadPoolExecutor() as executor:
        executor.map(process_date, date_list)


if __name__ == '__main__':
    main()
