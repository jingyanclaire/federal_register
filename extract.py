import re
import glob
import pandas as pd
import os
import matplotlib.pyplot as plt

def makeDataframe(fileList):
    # Column names for the DataFrame
    columns = ['FR Doc. Number', 'Text', 'Section','Date','Department', 'Agency (If Applicable)' ]

    # Creating the DataFrame
    df = pd.DataFrame(fileList, columns=columns)
    print(df)
    
def find_department(fileList):
    department_names_list = read_agency_names_from_csv("agency_names.csv")
    for file in fileList:
        departmentFound=False
        text=file[1]
        lines_list = text.split("\n")
        lineCounter=0
        for index, line in enumerate(lines_list):
            if lineCounter <= 20:
                for department in department_names_list:
                    if not departmentFound:
                        departmentMatch=re.search(department, line, re.IGNORECASE)
                        if departmentMatch:
                            departmentFound=True
                            file.append(departmentMatch.group())
                        else:
                            newLine=line+lines_list[index+1]
                            newDepartmentMatch=re.search(department, newLine, re.IGNORECASE)
                            if newDepartmentMatch:
                                departmentFound=True
                                file.append(newDepartmentMatch.group())
            lineCounter=lineCounter+1
        lineCounter=1
        agencyPattern1=r"Agency\s*:\s*"
        agencyPattern2=r"Agency\s*:\s*([^.\n]*\.[^\n]*)"
        agencyFound=False
        for index, line in enumerate(lines_list):
            if lineCounter <= 20:
                if not agencyFound:
                    agency1Match=re.search(agencyPattern1, line, re.IGNORECASE)
                    if agency1Match:
                        while (not agencyFound) and (lineCounter<4):
                            agency2Match=re.search(agencyPattern2, line, re.IGNORECASE)
                            if agency2Match:
                                agencyFound=True
                                file.append(agency2Match.group())
                            line=line+lines_list[index+lineCounter]
                            lineCounter=lineCounter+1    
        if agencyFound==False:
            file.append("No Related Agency")
        

def read_agency_names_from_csv(file_path):
    df = pd.read_csv(file_path)
    return df['agency.name'].tolist()

def find_each_file(sectionDict, date):
    fileList=[]
    pattern = r"(FR\sDoc\.\s\d{4}\s*.*)"
    for key, value in sectionDict.items():
        lines_list = value.split("\n")
        for line in lines_list:
            matches=re.findall(pattern, line, re.IGNORECASE)
            if (len(matches)>0):
                for match in matches:
                    fileList[-1][0]=match
                    fileList[-1][2]=key
                    fileList.append(['',"", "",date])
            elif (len(fileList)>0):
                if fileList[-1][1]!= '':
                    fileList[-1][1]=fileList[-1][1]+"\n"+line
                else:
                    fileList[-1][1]=fileList[-1][1]+line
            elif (len(fileList)==0):
                fileList.append(["First Entry", line, key])
    return fileList    
                
def additionalSections(file_path, sectionDict):
    randRFound=False
    prFound=False
    noticeFound=False
    randRPattern = r"\d{1,5}\s*Federal\s*Register\s*\/\s*Vol\.\s*\d+\s*,\s*No\.\s*\d+\s*\/\s*\w+\s*,\s*\w+\s*\d+\s*,\s*\d+\s*\/\s*Rules\s+and\s+Regulations\s*"
    prPattern=r"\d{1,5}\s*Federal\s*Register\s*\/\s*Vol\.\s*\d+\s*,\s*No\.\s*\d+\s*\/\s*\w+\s*,\s*\w+\s*\d+\s*,\s*\d+\s*\/\s*Proposed\s+Rules\s*"
    noticePattern=r"\d{1,5}\s*Federal\s*Register\s*\/\s*Vol\.\s*\d+\s*,\s*No\.\s*\d+\s*\/\s*\w+\s*,\s*\w+\s*\d+\s*,\s*\d+\s*\/\s*Notices\s*"
    RRHeader=r'Rules\s*and\s*Regulations\s*Federal\s*Register\s*(?:[1-9]\d{0,3}|10000)'
    PRHeader=r'Proposed\s*Rules\s*Federal\s*Register\s*(?:[1-9]\d{0,3}|10000)'
    noticeHeader= r'Notices\s*Federal\s*Register\s*(?:[1-9]\d{0,3}|10000)'
    readerAids=r'Reader\s+Aids\s+Federal\s+Register'
    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            RRHeadermatches=re.findall(RRHeader, line, re.IGNORECASE)
            PRHeaderMatches=re.findall(PRHeader, line, re.IGNORECASE)
            noticeHeaderMatches=re.findall(noticeHeader, line, re.IGNORECASE)
            RRmatches=re.findall(randRPattern, line, re.IGNORECASE)
            prMatches=re.findall(prPattern, line, re.IGNORECASE)
            noticeMatches=re.findall(noticePattern, line, re.IGNORECASE)
            readerMatches=re.findall(readerAids, line, re.IGNORECASE)
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
    folder_path = r'C:\Users\vishp\Desktop\Python\FDR\Extracting_info\Dates/*.txt'
    sectionDict={'Rules and Regulations':'', 'Proposed Rules':'', 'Notices':''}
    text_files = glob.glob(folder_path)
    
    for file_path in text_files:
        sectionDict={'Rules and Regulations':'', 'Proposed Rules':'', 'Notices':''}
        date=os.path.basename(file_path).split('.txt')[0]
        additionalSections(file_path, sectionDict)
        fileList=find_each_file(sectionDict, date)
        find_department(fileList)
        makeDataframe(fileList)

if __name__ == "__main__":
    main()
    