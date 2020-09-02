import os
from getpass import getpass

try:
    import requests
    from urllib.parse import urlparse, parse_qs
except(ModuleNotFoundError):
    os.system("pip install requests")
    import requests
    from urllib.parse import urlparse, parse_qs
except Exception as e:
    print("encountered Error")
    print(e)
    input("")

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
    global headers
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
    print("this is just a helper file, run something else")

if __name__ == "__main__":
    main()
    input("all done! Press enter or close window to exit")