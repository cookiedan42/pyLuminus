from pyLuminusFunctions import *

class luminusVideo(object):
    def __init__(self,path,fileDict):
        self.path = path
        self.fileName = fileDict.get('fileName')
        self.mediaBase = fileDict.get('streamUrlPath').rsplit('/',1)[0]
        self.chunksPath = self.mediaBase + "/" + self.getChunkpath(fileDict.get('streamUrlPath'))
    
    def getChunkpath(self,streamPath):
        r = requests.get(streamPath)
        chunkKey = [a for a in r.text.split('\n') if 'chunklist' in a]
        if len(chunkKey) == 1:#there's so far only one chunklist to search?
                chunkKey = chunkKey[0]
        else:
            print('well this is new...')
        return chunkKey
    
    def download(self):
        r = requests.get(self.chunksPath)
        if not os.path.exists(self.path.rsplit(os.sep,1)[0]):
            os.makedirs(self.path.rsplit(os.sep,1)[0])
        elif os.path.exists(self.path):
            return(f"  Checking {self.path}\n  video exists")
        chunks = [i for i in r.text.split("\n") if ".ts" in i]
        with open(f"{self.path}","wb") as outfile:
            for chunk in chunks:
                outfile.write(requests.get(self.mediaBase + "/" + chunk).content)
        return (f"  Checking {self.path}\n -New video downloaded")

def sanitizeFileName(filename):
    for i in ["\"","*","<",">","?","\\","|","/",":"]:
        filename = filename.replace(i,"_")
    filename = filename.strip(' ')
    return filename

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
            print("Valid auth header!")
        elif r.status_code == 401:
            auth = ""
            print(f"Encountered HTTP Error {r.status_code}, invalid auth header")
        else:
            print(f"Encountered HTTP Error {r.status_code}, more debugging needed :( ")
            auth = "failed"
    else:
        auth = ""

    while auth=="":# if invalid auth.txt, take in user input and validate it
        print("\ntype help for instructions on getting auth header\ntype login for to login to luminus directly!")
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
        elif auth=="login":
            auth = login()
            if auth =="":
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
            print("Valid auth header!")
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

def login(): #domain login
    username = input("nusnetid with nusstu\\\n")
    password = getpass("enter password\n")
    VAFS_data = {'UserName': username, 'Password': password, 'AuthMethod': 'FormsAuthentication'}
    r1 = requests.post(
        'https://vafs.nus.edu.sg/adfs/oauth2/authorize'
        ,data=VAFS_data
        ,params = {
            "response_type":"code"
            ,"client_id":"E10493A3B1024F14BDC7D0D8B9F649E9-234390"
            ,"redirect_uri":"https://luminus.nus.edu.sg/auth/callback"
            ,"resource":"sg_edu_nus_oauth"
        }
    )
    if urlparse(r1.url).netloc == 'vafs.nus.edu.sg':
        print('incorrect login details.')
        return ""
    else:
        query_string = urlparse(r1.url).query
        code = parse_qs(query_string)['code'][0]
        ADFS_TOKEN_URL = 'https://luminus.nus.edu.sg/v2/api/login/adfstoken'
        ADFS_TOKEN_data = {
            'grant_type': 'authorization_code'
            ,'client_id': 'E10493A3B1024F14BDC7D0D8B9F649E9-234390'
            ,'resource': 'sg_edu_nus_oauth'
            ,'code': code
            ,'redirect_uri': 'https://luminus.nus.edu.sg/auth/callback' 
        }
        r2 = requests.post(ADFS_TOKEN_URL, data=ADFS_TOKEN_data)
        print('Successful login!')
        return("Bearer "+ r2.json()['access_token'])

def getAllMultimedia(path,moduleID):
    folderDict = {}
    r = luminusJSON(
        "https://luminus.nus.edu.sg/v2/api/multimedia/"
        ,{"populate":"contentSummary","ParentID":moduleID}
    )
    for item in r:
        if item.get('isExternalTool'):#panopto
            pass
        elif item.get('fileFormat')=='Video':#luminus video
            folderDict[item["name"]] = luminusVideo(f"{path}{os.sep}{sanitizeFileName(item['name'])}",item)
        else:#luminus folder
            folderDict[item["name"]] = getMultimediaFolder(f"{path}{os.sep}{sanitizeFileName(item['name'])}",item.get('id'))
    return folderDict

def getMultimediaFolder(path,folderID):
    folderDict = {}
    r = luminusJSON(
        f"https://luminus.nus.edu.sg/v2/api/multimedia/{folderID}/medias"
        ,{})
    for item in r:
        if item.get('isExternalTool'):#panopto
            pass
        elif item.get('fileFormat')=='Video':#luminus video
            folderDict[item["name"]] = luminusVideo(f"{path}{os.sep}{sanitizeFileName(item['name'])}",item)
        else:#luminus folder
            folderDict[item["name"]] = getMultimediaFolder(f"{path}{os.sep}{sanitizeFileName(item['name'])}",item.get('id'))
    return folderDict

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
    modulesID = [(sanitizeFileName(i['name']),i['id'])for i in fullModules]
    #---this is where filtering by module name would happen---

    print("Searching for videos")
    allMedia = {}
    for module in modulesID:
        moduleDict = {}
        allMedia[module[0]] = getAllMultimedia(f"{module[0]}{os.sep}multimedia",module[1])
    print("Downloading new videos")
    for i in treeParser(allMedia):
        print(i.download())
        break


if __name__ == "__main__":
    main()
    input("all done! Press enter or close window to exit")
