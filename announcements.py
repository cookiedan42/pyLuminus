from pyLuminusFunctions import *
from datetime import datetime,timezone

def cleanAnnouncements(i):
    return{
        "module":i.get('parent').get('name'),
        "title":i.get('title'),
        "displayFrom":i.get("displayFrom"),
        "description":i.get("description")
    }

def getAnnouncements(ID): #unused
    #get all announcements for a module
    r = luminusJSON(
        f"https://luminus.nus.edu.sg/v2/api/announcement/NonArchived/{ID}"
        ,{"sortby":"displayFrom DESC","populate":"creator,lastUpdatedUser,parent","titleOnly":"false"}
    )
    return r
    # outString = ""
    # for i in r:
    #     outString+= f"{i['title']}\n{i['description']}\n\n\n-------End of Announcement-------\n\n"
    # return outString

def main():
    global headers
    headers,fullModules = getAuth()
    modulesID = [(sanitizeFileName(i['name']),i['id'])for i in fullModules]
    #---this is where filtering by module name would happen---

    print("Searching for Announcements")
    #create filetree
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    for module in modulesID:
        allAnnouncements = []
        for module in modulesID:
            moduleID = module[1]
            allAnnouncements+= getAnnouncements(moduleID)
    allAnnouncements = [cleanAnnouncements(i) for i in allAnnouncements]
    allAnnouncements.sort(key=lambda x:x.get("displayFrom"))
    
    print("Announcements\n")
    for announcement in allAnnouncements:
        print(f"module:  {announcement.get('module')}\ntitle:    {announcement.get('title')}")
        print(f"{announcement.get('description')}\n{'-'*30}\n\n")

if __name__ == "__main__":
    main()
    input("all done! Press enter or close window to exit")
