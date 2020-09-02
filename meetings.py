from pyLuminusFunctions import *
from datetime import datetime,timezone
def meetingClean(i,module):
    return{
        "module":module,
        "name":i.get('name'),
        "startDate":i.get('startDate'),
        "endDate":i.get('endDate'),
        "joinURL":i.get('joinUrl'),
        "password":requests.get(
            f"https://luminus.nus.edu.sg/v2/api/zoom/Meeting/{i.get('id')}/MeetingPasswords"
            ,headers=headers).json().get('password')
    }



def main():
    global headers
    headers,fullModules = getAuth()
    modulesID = [(sanitizeFileName(i['name']),i['id'])for i in fullModules]
    #---this is where filtering by module name would happen---

    print("Searching for meetings")
    #create filetree
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    for module in modulesID:
        allMeetings = []
        for module in modulesID:
            moduleID = module[1]
            allMeetings+= luminusJSON(
                f"https://luminus.nus.edu.sg/v2/api/zoom/Meeting/{moduleID}/Meetings"
                ,{
                    "where":f"endDate >= \"{now}\"" #end after today
                    ,"limit":"5"
                    ,"offset":"0"
                    ,"sortby":"startDate asc"
                }
    )
    allMeetings = [meetingClean(i,[name for name,code in modulesID if code == i.get('moduleID')][0]) for i in allMeetings]
    allMeetings.sort(key = lambda x:x.get('endDate'))

    print("""
        upcoming meetings""")
    for meeting in allMeetings:
        print(f"""
        module:  {meeting.get('module')}
        name:    {meeting.get('name')}
        start:   {meeting.get('startDate')}
        end:     {meeting.get('endDate')}
        joinURL: {meeting.get('joinURL')}
        password:{meeting.get('password')}
        """)


if __name__ == "__main__":
    main()
    input("all done! Press enter or close window to exit")
