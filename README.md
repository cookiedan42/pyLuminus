
<u>requirements</u>
- python
- requests package --> pip install requests

login   
type login when prompted for auth code  
enter nusstu\username and password  
magic happens

<u>how to get auth header</u>     
open a logged in session of luminus     
press f12 to open devtools      
go to network tab       
press <ctrl + R> or <f5> to refresh page and get network info   
look for a request that has an authorization header   
copy the authorization header in the request Headers sidebar    
Copy it--> should look something like "Bearer ......"   

Or just type help when prompted for the auth header