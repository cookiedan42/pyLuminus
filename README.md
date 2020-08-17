Luminus is very decentralised and searching for new things gets annoying   
these are a few tools written in python to centralise these resources   




<u>requirements</u>
- python
- requests package --> pip install requests


`files.py`    
- download all files from all modules

`multimedia.py`   
- download all multimedia from all modules
- currently only works for luminus native, not panopto

`meetings.py`   
- gets links of upcoming meetings and their passwords


login   
type login when prompted for auth code  
enter nusstu\username and password  
magic happens

<u>alternative how to get auth header</u>     
open a logged in session of luminus     
press f12 to open devtools      
go to network tab       
press <ctrl + R> or <f5> to refresh page and get network info   
look for a request that has an authorization header   
copy the authorization header in the request Headers sidebar    
Copy it--> should look something like "Bearer ......"   

Or just type help when prompted for the auth header
  
  
Still an early MVP, major changes have and will continue to happen
