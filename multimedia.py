from pyLuminusFunctions import *

class luminusVideo(object):
    def __init__(self,path,fileDict):
        self.path = path
        if os.path.splitext(fileDict.get('name'))[1] == "":
            self.path += os.path.splitext(fileDict.get('fileName'))[1]
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


if __name__ == "__main__":
    main()
    input("all done! Press enter or close window to exit")
