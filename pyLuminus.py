#TODO: filter by module code
#TODO: download multimedia
#TODO: error handling for all the other http codes
#TODO: error handling in general
#TODO: turn repeated check code into checkauth function
#TODO: automate pip install requests
#TODO: make a update auth header function
#TODO: turn this into a command line thing




try:
    import requests
except:
    print("unable to import requests\ntry running < pip install requests > in command line to install it")
import os

class luminusFile(object):
    # this data is all we need to download files
    # all the rest of code is to create this object
    def __init__(self,path,link,name):
        self.path = path
        self.dlLink = link
        self.name = name

    def download(self):
        if os.path.isfile(self.path):
            return(f'--Checking {self.path}\n--file already exists')
        r = requests.get(self.dlLink,headers=headers)
        if not os.path.exists(self.path.rsplit(os.sep,1)[0]):
            os.makedirs(self.path.rsplit(os.sep,1)[0])
        with open(self.path,"wb") as dlFile:
            dlFile.write(r.content)
            return(f'--Checking {self.path}\n !New file downloaded!')

class luminusMultimedia(object):#placeholder for multimedia downloads
    def __init__(self):
        pass
    def download(self):
        pass

def getAnnouncements(ID): #unused
    #get all announcements for a module
    r = luminusJSON(
        f"https://luminus.nus.edu.sg/v2/api/announcement/NonArchived/{ID}"
        ,{"sortby":"displayFrom DESC","populate":"creator,lastUpdatedUser,parent","titleOnly":"false"}
    )
    outString = ""
    for i in r:
        outString+= f"{i['title']}\n{i['description']}\n\n\n-------End of Announcement-------\n\n"
    return outString

def luminusJSON(target,params):#wrapper to make calling luminus API nicer
    r = requests.get(
        target
        ,headers=headers
        ,params=params
    )
    if r.status_code == 200:
        if r.json()['total']>0:
            return r.json()['data']
        else: #force return list for downstream reasons
            return []
    elif r.status_code == 401:
        return "Error 401: restart and update Auth Header"
    else:
        print(f"Error {r.status_code}")
        return r.status_code

def getAuth():
    if os.path.isfile("auth.txt"): #test saved auth header
        with open("auth.txt","r") as authFile:
            auth = authFile.read()
        headers = {
            "Authorization": auth
            ,"DNT":"1"
        }
        r = requests.get(
            "https://luminus.nus.edu.sg/v2/api/module/"
            ,headers=headers,
            params={"populate":"Creator,termDetail,isMandatory"}
        )
        if r.status_code == 200:
            print("auth Header works!")
        elif r.status_code == 401:
            auth = ""
            print(f"Encountered HTTP Error {r.status_code}, invalid auth header")
        else:
            print(f"Encountered HTTP Error {r.status_code}, more debugging needed :( ")
            auth = "failed"
    else:
        auth = ""
    
    while auth=="":# if invalid auth.txt, take in user input and validate it
        print("type help for instructions on getting auth header")
        auth = input("Please paste a new auth header\n")

        if auth =="help":
            print('''
            open a logged in session of luminus
            press f12 to open devtools
            go to network tab
            press <ctrl + R> or <f5> to refresh page and get network info
            look for a request to luminus.nus.edu.sg and click on it
            find the authorization header in the request Headers sidebar
            Copy it--> should look something like "Bearer ......"
            ''')
            auth = ""
            continue

        headers = {
            "Authorization": auth
            ,"DNT":"1"
        }
        r = requests.get(
            "https://luminus.nus.edu.sg/v2/api/module/?populate=Creator%2CtermDetail%2CisMandatory"
            ,headers=headers
        )
        if r.status_code == 200:
            print("auth Header works!")
        elif r.status_code == 401:
            auth = ""
            print(f"Encountered HTTP Error {r.status_code}, invalid auth header")
        else:
            print(f"Encountered HTTP Error {r.status_code}, more debugging needed :( ")
            auth = ""
        if auth!="":
            with open("auth.txt","w") as authFile:
                authFile.write(auth)
    return headers,r.json()["data"]

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
        if item.get("sortFilesBy"):#is a subfolder
            if item.get('isActive')==True:
                subFolderID = item["id"]
                outDict[path+os.sep+item['name']] = parseFolder(path+os.sep+item['name'],subFolderID)
        else: #file
            outDict[item["fileName"]] = parseFile(path+os.sep+item['name'],item["fileName"],item["id"])
    return outDict

def parseFile(path,fileName,fileID):
    dl = requests.get("https://luminus.nus.edu.sg/v2/api/files/file/"+fileID+"/downloadurl",headers=headers).json()['data']
    return luminusFile(path,dl,fileName)

def treeParser(tree):
    #flattens tree of module files
    a =  [treeParser(i)if type(i) == dict else i for i in tree.values()]
    b = []
    for i in a:
        if type(i)==list:
            b+=i
        else:
            b+=[i]
    return b

def main():
    global headers
    headers,fullModules = getAuth()
    modulesID = [(i['name'].replace("/","_"),i['id'])for i in fullModules] #sanitise CS2030/CS2030S to prevent directory spam
    #---this is where filtering by module name would happen---

    print("Searching for files")
    #create filetree
    moduleFiles = {}
    for module in modulesID:
        #module is [name,ID]
        moduleFiles[module[0]] = parseFolder(module[0],module[1])

    print("downloading new files")
    #download all files in flattened file tree
    for i in treeParser(moduleFiles):
        print(i.download())

if __name__ == "__main__":
    main()
    input("all done! Press enter or close window to exit")