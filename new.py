import fitz
import requests
import io
import os
import re
from concurrent.futures import ThreadPoolExecutor

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


def make_folder(year, month, date, pdf_stream):
    folder_path = f"D:\\pycharm\\pythonProject\\pdf-txt\\FR-{year}\\{month}"
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    get_txt(date, pdf_stream, folder_path)


def process_date(year, month, day):
    if day < 10:
        day_str = f"0{day}"
    else:
        day_str = str(day)
    if month < 10:
        month_str = f"0{month}"
    else:
        month_str = str(month)

    date = f"{year}-{month_str}-{day_str}"
    url = f"https://www.govinfo.gov/content/pkg/FR-{date}/pdf/FR-{date}.pdf"
    response = requests.get(url)
    if response.status_code == 200 and response.url == url:
        pdf_stream = io.BytesIO(response.content)
        make_folder(year, month_str, date, pdf_stream)
        pdf_stream.close()
    response.close()


def main():
    with ThreadPoolExecutor() as executor:
        for year in range(2000, 2001):
            for month in range(1, 13):
                days_in_month = 31
                if month == 2:
                    if year % 4 == 0 and (year % 100 != 0 or year % 400 == 0):
                        days_in_month = 29
                    else:
                        days_in_month = 28
                elif month in [4, 6, 9, 11]:
                    days_in_month = 30
                # executor.map(process_date, [year] * days_in_month, [month] * days_in_month, range(1, days_in_month + 1))
                process_date(1990, 1, 3)


if __name__ == '__main__':
    main()