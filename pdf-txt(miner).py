import time
import requests
import io
import os
import re
from concurrent.futures import ThreadPoolExecutor
from pdfminer.high_level import extract_pages
from pdfminer.layout import LTTextContainer, LAParams, LTTextBox, LTTextLine
from retrying import retry

# RE = r'\s*F\s*e\s*d\s*e\s*r\s*a\s*l\s*R\s*e\s*g\s*i\s*s\s*t\s*e\s*r\s*/\s*V\s*o\s*l\s*'
RE = r'\s*F\s*[éèêëeE]\s*d\s*[éèêëeE]\s*r\s*a\s*l\s*R\s*[éèêëeE]\s*g\s*[LIil1íìîï]\s*s\s*t\s*[éèêëeE]\s*r\s*/\s*V\s*[Oo0óòôöõøœ]\s*[LIil1íìîï]\s*'


@retry(stop_max_attempt_number=3, wait_fixed=2000)
def fetch_response(url):
    response = requests.get(url)
    if response.status_code == 200 and len(response.content) > 1000:
        return response
    else:
        response.raise_for_status()

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


def get_column_bounds(page_layout, header_end_y):
    words = []
    for obj in page_layout:
        if isinstance(obj, LTTextContainer):
            for line in obj:
                if isinstance(line, (LTTextBox, LTTextLine)):
                    start_x = line.x0
                    end_x = line.x1
                    words.append({
                        'x0': start_x,
                        'x1': end_x
                    })

    words = sorted(words, key=lambda word: word['x0'])

    bounds = [0]
    for i, word in enumerate(words[:-1]):
        current_word = words[i]
        next_word = words[i + 1]
        if next_word['x0'] - current_word['x1'] > 50:
            bounds.append((current_word['x1'] + next_word['x0']) / 2)

    bounds.append(page_layout.width)

    # Ensure all boundaries are within the page boundaries
    bounds = [max(0, b) for b in bounds]
    bounds = [min(page_layout.width, b) for b in bounds]

    return bounds

def get_txt(date, pdf_file, folder_path):
    print(f"Extracting text from PDF for date: {date}")

    laparams = LAParams()

    lines = []
    for page_layout in extract_pages(pdf_file, laparams=laparams):
        # 获取页眉的位置
        matching_words = [obj for obj in page_layout if isinstance(obj, LTTextContainer) and re.match(RE, obj.get_text())]
        header_end_y = max([word.bbox[3] for word in matching_words]) if matching_words else 0

        # 处理多列
        bounds = get_column_bounds(page_layout, header_end_y)
        for i in range(len(bounds) - 1):
            left, right = bounds[i], bounds[i + 1]
            # 提取段落
            for obj in page_layout:
                if isinstance(obj, LTTextContainer):
                    x, y, x1, y1 = obj.bbox
                    if left < x1 and right > x:
                        for line in obj.get_text().split('\n'):
                            if re.match(RE, line):
                                line = fix_vowels_line(line)
                            lines.append(line)

    with open(f'{folder_path}/{date}.txt', 'w', encoding='utf-8') as file:
        file.write('\n'.join(lines))


def make_folder(year, month, date, pdf_file):
    folder_path = f"D:\\pycharm\\pythonProject\\pdf-txt\\FR(miner)\\FR-{year}\\{month}"
    # folder_path = f"D:\\pycharm\\pythonProject\\pdf-txt\\FR-{year}\\{month}"
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    get_txt(date, pdf_file, folder_path)


def process_date(year, month, day):
    global response
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
    print(f"Downloading file for date: {date}")
    try:
        response = fetch_response(url)
        pdf_file = io.BytesIO(response.content)
        make_folder(year, month_str, date, pdf_file)
    except requests.exceptions.RequestException as e:
        print(f"Failed to get response for the date {date}, error: {e}")
    finally:
        response.close()
        time.sleep(1)


def is_empty(text):
    return len(text.strip()) == 0


def check_and_redownload_empty_files(folder_path):
    redownloaded_files = []
    redownload_needed = False
    for root, ds, fs in os.walk(folder_path):
        for file_name in fs:
            if file_name.endswith('.txt'):
                with open(os.path.join(root, file_name), 'r', encoding='utf-8') as file:
                    content = file.read(30)
                    if is_empty(content):
                        date_info = re.search(r'FR-(\d{4})-(\d{2})-(\d{2})', file_name)
                        if date_info:
                            year, month, day = map(int, date_info.groups())
                            print(f"Redownloading empty file for date: {year}-{month}-{day}")
                            process_date(year, month, day)
                            redownloaded_files.append(file_name)
                            redownload_needed = True
    if redownload_needed:
        print("Redownloaded files:")
        for file in redownloaded_files:
            print(file)
    return redownload_needed


def main():

    try:
        for year in range(1969, 1980):
            for month in range(1, 13):
                with ThreadPoolExecutor(max_workers=3) as executor:
                    days_in_month = 31
                    if month == 2:
                        if year % 4 == 0 and (year % 100 != 0 or year % 400 == 0):
                            days_in_month = 29
                        else:
                            days_in_month = 28
                    elif month in [4, 6, 9, 11]:
                        days_in_month = 30
                    executor.map(process_date, [year] * days_in_month, [month] * days_in_month,
                                 range(1, days_in_month + 1))
                    for _ in range(3):
                        redownload_needed = check_and_redownload_empty_files(
                            f"D:\\pycharm\\pythonProject\\pdf-txt\\FR(miner)\\FR-{year}\\{str(month).zfill(2)}")
                        if not redownload_needed:
                            break
    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == '__main__':
    main()
