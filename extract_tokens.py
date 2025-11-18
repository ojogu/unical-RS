import json

req_str = '["",{"Vary":"Origin","Set-Cookie":"DSPACE-XSRF-COOKIE=; Max-Age=0; Expires=Thu, 01 Jan 1970 00:00:10 GMT; Path=/server; HttpOnly; SameSite=Lax","DSPACE-XSRF-TOKEN":"6e99db95-77a1-45a5-a092-bc8b8b4d2426","Authorization":"Bearer eyJhbGciOiJIUzI1NiJ9.eyJlaWQiOiJkZjljZTYwYi00NGE1LTQyYzMtOWQ5Zi1mYWNlYzIwNjJiYjAiLCJzZyIYV10sImV4cCI6MTc2MzM4NzE5NiwiYXV0aGVudGljYXRpb25NZXRob2QiOiJwYXNzd29yZCJ9.Z9hXa1i1uTi_-goyftPK6C3yc3Zwj6PdU1LNFq97PiE","X-Content-Type-Options":"nosniff","X-XSS-Protection":"0","Cache-Control":"no-cache, no-store, max-age=0, must-revalidate","Pragma":"no-cache","Expires":"0","X-Frame-Options":"DENY","Content-Length":"0","Date":"Mon, 17 Nov 2025 13:16:36 GMT"}]'

# The string is not valid JSON directly because of the single quotes around dictionary keys and values.
# It looks like a Python list representation. We can use ast.literal_eval to safely parse it.
import ast

parsed_list = ast.literal_eval(req_str)

# The dictionary is the second element in the list
headers = parsed_list[1]

authorization_token = headers.get("Authorization")
dspace_xsrf_token = headers.get("DSPACE-XSRF-TOKEN")

print(f"Authorization: {authorization_token}")
print(f"DSPACE-XSRF-TOKEN: {dspace_xsrf_token}")
