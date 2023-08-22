import re
import glob
import pandas as pd
import os

def makeDataframe(fileList):
    # Column names for the DataFrame
    columns = ['FR Doc. Number', 'Text', 'Section','Date','Department', 'Agency (If Applicable)' ]

    # Creating the DataFrame
    df = pd.DataFrame(fileList, columns=columns)

    #print entire dataframe
    print(df)
    #print first 40 entries of the department column
    #print(df['Department'].head(40))
    #print first 40 entries of the agency column
    #print(df['Agency (If Applicable)'].head(40))
    #print first 40 entries of the Section column
    print(df['Section'].head(60))
    #print first 40 entries of the Date column
    #print(df['Date'].head(40))
    #print first 40 entries of the text column
    #print(df['Text'].head(40))

def find_department_agency(fileList):

    #for every entry found n the entry list
    for file in fileList:
        #split after each line and store each line to a list
        text=file[1]
        lines_list = text.replace("\n",' ')

        #find department for the entry
        find_dep_agency(file, lines_list)

        #find agency for the entry
        # find_dep_agency(file, lines_list, agency_names_list, 'Agency')
        #agencyPattern1=r"Agency\s*:\s*"
        #agencyPattern2=r"Agency\s*:\s*([^.\n]*\.[^\n]*)"

def find_dep_agency(file, lines_list):
    #initialize variables for whether the dep/agency has been found as well as the line counter
    if lines_list.find('AGENCY :')!=-1:
        #extract the place that agency would exist
        AGENCY=lines_list[lines_list.find('AGENCY :')+8:lines_list.find('ACTION :')]
    else:
        AGENCY=''
    if lines_list.find('–P')!=-1 or lines_list.find('from further violations of the Act.')!=-1: #to get font letter starting place
        if lines_list.find('–P')!=-1:
            index=lines_list.find('–P')
            skew=3
        else:
            index=lines_list.find('from further violations of the Act.')
            skew=35 #for every starting chapter page

        #by comparing the starting text with extracted agency
        aa=lines_list[index+skew:index+100]
        bb=aa.split(' ')
        departement=''
        for i in bb:
            if i.isupper():
                departement=departement+i+' '
            else:
                break
        departement_new=departement[:-1]
        if departement_new==AGENCY.upper()[:-1]:
            file.append("No Department Found")
        else:
            file.append(departement[:-1])
        if AGENCY=='':
            file.append("No Agency Found")
        else:
            file.append(AGENCY)


def easierRegEx(string):
    #take every word in the string being searched for, add a \s* after
    regexDep=''
    departmentWords = string.split()
    for index,word in enumerate(departmentWords):
        regexDep=regexDep+word+'\s*'
    return regexDep

#read either department or agency names from a given csv
def read_agency_names_from_csv(file_path,name):
    df = pd.read_csv(file_path)
    return df[name].tolist()

#find each entry within every section of a file
def find_each_file(sectionDict, date):
    #intialize list to store lists for every entry
    fileList=[]
    #regex pattern for FR Doc. followed by four digits
    pattern = r"(FR Doc. 04)"
    #for every section, and related text found in the dictionary
    for key, value in sectionDict.items():
        #split every line and store into list
        lines_list = value.split("\n")
        for line in lines_list:
            #find if line contains FR Doc at the end
            match=re.search(pattern, line, re.IGNORECASE)
            #if it contains FR Doc
            if match:
                #add the FR Doc Number as the number of the last entry as an indentifier
                fileList[-1][0]=match
                #append a new entry
                fileList.append(['',"", "",date])
            #if not the first entry in the list
            elif (len(fileList)>0):
                #if not the first line to be added as the text of the entry
                if fileList[-1][1]!= '':
                    #append line to the end of the entry with a new line character
                    fileList[-1][1]=fileList[-1][1]+"\n"+line
                    #append key of the entry
                    fileList[-1][2]=key
                else:
                    fileList[-1][1]=fileList[-1][1]+line
            #if first entry being analyzed, put placeholder for FR Doc number and append info
            elif (len(fileList)==0):
                fileList.append(["First Entry", line, key, date])
    return fileList

#find every section within a certain file
def additionalSections(file_path, sectionDict):
    #initialize boolean variables for each section
    randRFound=False
    prFound=False
    noticeFound=False
    #patterns for each sections's regular page header
    randRPattern = r"\d{1,5}\s*Federal\s*Register\s*\/\s*Vol\.\s*\d+\s*,\s*No\.\s*\d+\s*\/\s*\w+\s*,\s*\w+\s*\d+\s*,\s*\d+\s*\/\s*Rules\s+and\s+Regulations\s*"
    prPattern=r"\d{1,5}\s*Federal\s*Register\s*\/\s*Vol\.\s*\d+\s*,\s*No\.\s*\d+\s*\/\s*\w+\s*,\s*\w+\s*\d+\s*,\s*\d+\s*\/\s*Proposed\s+Rules\s*"
    noticePattern=r"\d{1,5}\s*Federal\s*Register\s*\/\s*Vol\.\s*\d+\s*,\s*No\.\s*\d+\s*\/\s*\w+\s*,\s*\w+\s*\d+\s*,\s*\d+\s*\/\s*Notices\s*"
    #patterns for each section's first page
    RRHeader=r'Rules\s*and\s*Regulations\s*Federal\s*Register\s*(?:[1-9]\d{0,3}|10000)'
    PRHeader=r'Proposed\s*Rules\s*Federal\s*Register\s*(?:[1-9]\d{0,3}|10000)'
    noticeHeader= r'Notices\s*Federal\s*Register\s*(?:[1-9]\d{0,3}|10000)'
    #pattern for reader aids
    readerAids=r'Reader\s+Aids\s+Federal\s+Register'
    #read text file and read line by line
    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            #find if there is a match for the pattern within the line
            RRHeadermatches=re.findall(RRHeader, line, re.IGNORECASE)
            PRHeaderMatches=re.findall(PRHeader, line, re.IGNORECASE)
            noticeHeaderMatches=re.findall(noticeHeader, line, re.IGNORECASE)
            RRmatches=re.findall(randRPattern, line, re.IGNORECASE)
            prMatches=re.findall(prPattern, line, re.IGNORECASE)
            noticeMatches=re.findall(noticePattern, line, re.IGNORECASE)
            readerMatches=re.findall(readerAids, line, re.IGNORECASE)
            #if there is a reader match, exit loop
            #if there is a match for one of the sections, store into that section's value within the dictionary
            if readerMatches:
                noticeFound=False
                prFound=False
                randRFound=False
            elif (len(RRmatches)>0) or (len(RRHeadermatches)>0):
                randRFound=True
                prFound=False
                noticeFound=False
                sectionDict['Rules and Regulations']=sectionDict['Rules and Regulations']+line
            elif (len(prMatches)>0) or (len(PRHeaderMatches)>0):
                prFound=True
                randRFound=False
                noticeFound=False
                sectionDict['Proposed Rules']=sectionDict['Proposed Rules']+line
            elif (len(noticeMatches)>0) or (len(noticeHeaderMatches)>0):
                noticeFound=True
                prFound=False
                randRFound=False
                sectionDict['Notices']=sectionDict['Notices']+line
            elif randRFound:
                sectionDict['Rules and Regulations']=sectionDict['Rules and Regulations']+line
            elif noticeFound:
                sectionDict['Notices']=sectionDict['Notices']+line
            elif prFound:
                sectionDict['Proposed Rules']=sectionDict['Proposed Rules']+line


def main():
    #folder containing text files that need analysis
    folder_path = r'2005-01-03.txt'
    #list containing every file path within the folder
    text_files = glob.glob(folder_path)

    #for every file in the folder contain the files that are being analyzed
    for file_path in text_files:
        #remake the dictionary
        sectionDict={'Rules and Regulations':'', 'Proposed Rules':'', 'Notices':''}
        #find date using the text file's name
        date=os.path.basename(file_path).split('.txt')[0]
        #find sections
        additionalSections(file_path, sectionDict)
        #find each entry
        fileList=find_each_file(sectionDict, date)
        #find department and/or agency
        find_department_agency(fileList)
        #store entry data into a dataframe
        makeDataframe(fileList)


if __name__ == "__main__":
    main()
