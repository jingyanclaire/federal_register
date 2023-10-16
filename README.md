# federal_register
analyzation of  federal register

pdf-txt's file:

"Find_cid.py" is used to find the txt file which just contain the cid code, after running the program, it will produce a txt file which contain all the cid code txt files' path, such as: "D:\pycharm\pythonProject\pdf-txt\FR(miner)\FR-2000\01\2000-01-03.txt".

"Find_empty.py" is used to check if there are any txt files which is empty because of the bad internet, after running the program, it will produce a txt file which contain all the empty txt files' name, such as "1939-08-18.txt".

"get_empty.py" is used to get the empty file, which need user run the "Find_empty.py" firstly to get the txt file which contain all the empty txt and then run the get_empty.py by changing the txt file's path.

"pdf-txt(miner).py" is used to transfer pdf file to the txt file, which use the pdfminer package. The txt file between 1936-1999 in oneDrive should be used this package.

"pdf-txt(pypdf2).py" is used to transfer pdf file to the txt file, which use the pypdf2 package. The txt file between 2000-2023 in oneDrive should be used this package.

"pdf-txt(pymupdf).py" is usdd to transfer pdf file to the txt file, which use the pymupdf package. None txt file use this one but it's the fastest package to transfer, only can be used after 2000 years
