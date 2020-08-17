from pyLuminusFunctions import *

class luminusFile(object):
    # this data is all we need to download files
    # all the rest of code is to create this object
    def __init__(self,path,link,name):
        self.path = path
        self.dlLink = link
        self.name = name

    def download(self):
        if os.path.isfile(self.path):
            return(f'  Checking {self.path}\n -file already exists')
        r = requests.get(self.dlLink,headers=headers)
        if not os.path.exists(self.path.rsplit(os.sep,1)[0]):
            os.makedirs(self.path.rsplit(os.sep,1)[0])
        with open(self.path,"wb") as dlFile:
            dlFile.write(r.content)
            return(f'  Checking {self.path}\n! New file downloaded!')


def parseFolder(path,folderID): #search a folder for subfolders and files
    outDict = {}
    folderItems = luminusJSON(
        "https://luminus.nus.edu.sg/v2/api/files/"
        ,{"populate":"totalFileCount,subFolderCount,TotalSize","ParentID":folderID}
    )
    folderItems+=luminusJSON(
        f"https://luminus.nus.edu.sg/v2/api/files/{folderID}/file"
        ,{"populate":"Creator,lastUpdatedUser,comment"}
    )
    for item in folderItems:
        if "isTurnitinFolder" in item.keys():#is a subfolder
            if item.get('isActive')==True:
                subFolderID = item["id"]
                outDict[path+os.sep+sanitizeFileName(item['name'])] = parseFolder(path+os.sep+sanitizeFileName(item['name']),subFolderID)
        else: #file
            outDict[sanitizeFileName(item["fileName"])] = parseFile(path+os.sep+sanitizeFileName(item['name']),sanitizeFileName(item["fileName"]),item["id"])
    return outDict

def parseFile(path,fileName,fileID):
    dl = requests.get("https://luminus.nus.edu.sg/v2/api/files/file/"+fileID+"/downloadurl",headers=headers).json()['data']
    return luminusFile(path,dl,fileName)

def main():
    global headers
    headers,fullModules = getAuth()
    modulesID = [(sanitizeFileName(i['name']),i['id'])for i in fullModules]
    #---this is where filtering by module name would happen---

    print("Searching for files")
    #create filetree
    moduleFiles = {}
    for module in modulesID:
        #module is [name,ID]
        moduleFiles[module[0]] = parseFolder(module[0],module[1])
    print("Downloading new files")
    #download all files in flattened file tree
    for i in treeParser(moduleFiles):
        print(i.download())


if __name__ == "__main__":
    main()
    input("all done! Press enter or close window to exit")
