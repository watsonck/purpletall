import requests,json

json_string = requests.get('http://purpletall.cs.longwood.edu:5000/1/LIST').text
obj = json.loads(json_string)
print(obj['metadata']['project'])
print(obj['tasks'][0]['name'])
