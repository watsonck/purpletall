import requests,json

print(requests.get('http://purpletall.cs.longwood.edu:5000/1/add?name={Bug1}&desc={This%20bug%20is%20in%20controller}&time={2019-05-1}&bug={true}').text)
#json_string = requests.get('http://purpletall.cs.longwood.edu:5000/1/move?id=6&stage={DONE}').text
#print(json_string);
#obj = json.loads(json_string)
#print(obj)
#print(obj['metadata']['stages']['1'])
#print(obj['stages']['0'][0]['name'])

#obj[stages][which stage][which task in stage][which item in task]
