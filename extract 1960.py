import re
import glob
import pandas as pd
import os
import concurrent.futures


# take every word in the string being searched for, add a [.,\s]* after
# after every letter add a \s{0,3}
def easierRegEx(string):
    LetterSeparator = ''
    regexDep = ""
    # for each letter in the string, add a \s{0,3}
    # allows for zero-three spaces between the letters to account for encoding errors with spacing
    for letter in string:
        if (letter != ''):
            LetterSeparator = LetterSeparator + letter + '\s{0,3}'
    # for each word in the string, add a [.,\s]*
    # allows for zero or more occurances of a white space, period or comma between words to account for 90s agency formatting
    departmentWords = LetterSeparator.split()
    for word in departmentWords:
        regexDep = regexDep + word + '[.,\s]*'
    return regexDep


# find each entry within every section of a file
def find_each_file(file_path, date):
    # intialize list to store lists for every entry
    fileList = []
    # regex pattern for FR Doc. followed by four digits
    # pattern = r"([FP]\s*R\s*D{1,2}\s*o{1,2}\s*c{1,2}\s*.+ f{1,2}\s*((i{1,2}\s*[f,l]{1,2}\s*)|(U\s*))e{1,2}\s*d{1,2}\s*.+[apfu].*[mn])"
    pattern = r"([FP]\s*\.\s*R\s*\.\s*D{1,2}\s*o{1,2}\s*c{1,2}\s*.+ f{1,2}\s*((i{1,2}\s*[f,l]{1,2}\s*)|(U\s*))e{1,2}\s*d{1,2})"
    linesList = []
    # readlines from the the file into a list
    with open(file_path, 'r', encoding='utf-8') as file:
        linesList = file.readlines()
    last = 0
    # find the last FR doc and remove everything after
    findLast = True
    for j in range(len(linesList)):
        if findLast:
            match = re.search(pattern, linesList[len(linesList) - 1 - j], re.IGNORECASE)
            if match:
                last = len(linesList) - j
                findLast = False
    # set i to 1000 as first 1000-4000 lines are typically the table of contents
    i = 1000
    # search through every line
    while i < (len(linesList) - 1):
        line = linesList[i]
        i = i + 1
        # find if line contains FR Doc pattern
        match = re.search(pattern, line, re.IGNORECASE)
        # if it contains FR Doc pattern
        if match:
            # add the FR Doc Number as the number of the last entry as an indentifier
            fileList[-1][0] = match.group(1)
            fileList[-1][1] = fileList[-1][1] + line
            # append a new entry
            fileList.append(['', "", "", date, "", ""])
            # if not the first entry in the list
        elif (len(fileList) > 0) and (i < last):
            # if not the first line to be added as the text of the entry
            if fileList[-1][1] != '':
                # append line to the end of the entry with a new line character
                fileList[-1][1] = fileList[-1][1] + line
                # append key of the entry
            else:
                fileList[-1][1] = fileList[-1][1] + line
        # if first entry being analyzed, put placeholder for FR Doc number and append info
        elif (len(fileList) == 0):
            fileList.append(["First Entry", line, "", date, "", ""])
    return fileList


# find all of headers that show what section the page is on
def findSectionHeaders(file):
    sectionFound = False
    # patterns for each section's headers
    NoticePattern = "^" + easierRegEx("NOTICES") + "$"
    PRPattern = "^" + easierRegEx("PROPOSED RULE MAKING") + "$"
    randRPattern = "^" + easierRegEx("RULES AND REGULATIONS") + "$"
    # search through everyone line to find what section the file is in
    linesList = file[1].split('\n')
    for line in linesList:
        if not (sectionFound):
            # Find which section it most likely is
            RRHeadermatch = re.search(randRPattern, line)
            PRHeaderMatch = re.search(PRPattern, line)
            noticeHeaderMatch = re.search(NoticePattern, line)
            # store into right section and return back to loop
            if (RRHeadermatch):
                sectionFound = True
                section = 'Rules and Regulations'
            elif (PRHeaderMatch):
                sectionFound = True
                section = "Proposed Rule Making"
            elif (noticeHeaderMatch):
                sectionFound = True
                section = "Notices"
            else:
                section = "NOPE"
    return section


# Rules and Regulations is the only section that has the chapter or subchapter typically mentioned
# use this fact to make additions where not initially found
def findRulesAndRegulations(file):
    if file[2] == ("NOPE"):
        # matches Chapter (roman numeral)
        randRPattern = easierRegEx("CHAPTER") + "(XC|XL|L?X{0,3})(IX|IV|V?I{0,3})— "
        randRPattern2 = easierRegEx("SUBCHAPTER")
        linesList = file[1].split('\n')
        for line in linesList:
            RRHeadermatch = re.search(randRPattern, line, re.IGNORECASE)
            RRHeadermatch2 = re.search(randRPattern2, line, re.IGNORECASE)
            if RRHeadermatch or RRHeadermatch2:
                file[2] = "Rules and Regulations"


# read either department or agency names from a given csv
def read_agency_names_from_csv(file_path, name):
    df = pd.read_csv(file_path)
    return df[name].tolist()


# find either department or agency being searched for and store into dataframe
def find_dep_agency(file, lines_list, names_list, dep_ag, fileList, fileIndex):
    # initialize variables for whether the dep/agency has been found as well as the line counter
    Found = False
    lineLimit = 30
    # for every line and index within the lines list
    for index, line in enumerate(lines_list):
        # search only the first 20 lines
        if index <= lineLimit:
            if len(line) < 3:
                lineLimit = lineLimit + 1
            # for every name of dep/agency within the csv
            for name in names_list:
                # create a easier to find regex statement
                name = name[:43]
                regExDep = easierRegEx(name)
                # as long a match hasn't been found yet, keep searching
                if not Found:
                    # use regEx to search within the line
                    match = re.search(regExDep, line, re.IGNORECASE)
                    # if found, stop loop and store as the dep/agency for the entry
                    if match:
                        Found = True
                        if (match.group().isupper()):
                            file[dep_ag] = (name.upper())
                        else:
                            file[dep_ag] = name
                    # if not found
                    else:
                        # if not on the last line of the entry
                        if (index + 1) < (len(lines_list) - 1):
                            # combine former line and line after into a new line
                            newLine = line + lines_list[index + 1]
                            # use regEx to search within the line
                            newMatch = re.search(regExDep, newLine, re.IGNORECASE)
                            # if found, stop loop and store as the dep/agency for the entry
                            if newMatch:
                                Found = True
                                if (newMatch.group().isupper()):
                                    file[dep_ag] = (name.upper())
                                else:
                                    file[dep_ag] = name
                                    # if still not found, dep/ag was not found
    if not Found:
        file[dep_ag] = "Not Found"


# store department and agency names into pandas dataframes and start search for both
def find_department(fileList):
    # read each name in department csv to a list
    department_names_list = read_agency_names_from_csv("department_names_only (003).csv", 'department.name')

    # read each name in the agency csv to a list
    agency_names_list = read_agency_names_from_csv("AgencyNamesOnly.csv", 'agency.name')

    # for every entry found in the entry list
    for index, file in enumerate(fileList):
        # split after each line and store each line to a list
        text = file[1]
        lines_list = text.split("\n")

        # find department for the entry
        find_dep_agency(file, lines_list, department_names_list, 4, fileList, index)

        # find agency for the entry
        find_dep_agency(file, lines_list, agency_names_list, 5, fileList, index)


# store collected data into dataframes
def makeDataframe(fileList):
    # Column names for the DataFrame
    columns = ['FR Doc. Number', 'Text', 'Section', 'Date', 'Department', 'Agency']

    df = pd.DataFrame(fileList, columns=columns)
    # create data frame without text
    csvDf = df.drop('Text', axis=1)
    print(df)
    # find all emtpy files
    empty = csvDf.loc[(df['Department'] == "Not Found") & (df['Agency'] == "Not Found")]
    # output directory
    directory = './output'
    # fileName for both files
    filename = str(csvDf.iloc[0]['Date']) + '.csv'
    textFileName = str(csvDf.iloc[0]['Date']) + 'text' + '.csv'
    emptyFileName = (csvDf.iloc[0]['Date']) + 'empty' + '.csv'
    # path to write output files
    file_path = os.path.join(directory, filename)
    file_pathTEXt = os.path.join(directory, textFileName)
    file_pathEmpty = os.path.join(directory, emptyFileName)
    # create folder if not present
    if not os.path.isdir(directory):
        os.mkdir(directory)
    # write dataframes to csv files
    csvDf.to_csv(file_path, index=True)
    df.to_csv(file_pathTEXt, index=True)
    empty.to_csv(file_pathEmpty, index=True)
    return df


def makeReplacements(fileList):
    for index, file in enumerate(fileList):
        notFound = True
        if (file[2] == 'NOPE') and index < (len(fileList)):
            i = 0
            while i < 5:
                i += 1
                if notFound and index + i < (len(fileList)):
                    goingDown = fileList[index + i][2]
                    j = 0
                    while j < 5:
                        j += 1
                        if notFound and index - i < (len(fileList)):
                            goingUp = fileList[index - i][2]
                            if goingDown == goingUp:
                                file[2] = goingUp
                                notFound = False


def analyze_file(filePath):
    # find date using the text file's name
    date = os.path.basename(filePath).split('.txt')[0]
    fileList = find_each_file(filePath, date)
    for file in fileList:
        file[2] = findSectionHeaders(file)
        findRulesAndRegulations(file)
    makeReplacements(fileList)
    find_department(fileList)
    df = makeDataframe(fileList)


def main():
    # folder containing text files that need analysis
    folder_path = r'D:\pycharm\pythonProject\pdf-txt\1969-12/*.txt'
    # list containing every file path within the folder
    text_files = glob.glob(folder_path)
    for file_path in text_files:
        analyze_file(file_path)


if __name__ == "__main__":
    main()
