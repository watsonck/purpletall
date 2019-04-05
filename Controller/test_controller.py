import requests,json

json_string = requests.get('http://purpletall.cs.longwood.edu:5000/1/LIST').text
obj = json.loads(json_string)
print(obj)
print(obj['metadata']['stages']['1'])
print(obj['stages']['0'][0]['name'])

#obj[stages][which stage][which task in stage][which item in task]
