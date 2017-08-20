import requests
import json
import numpy as np


headers = {'content-type': 'application/json'}
base_url = 'http://localhost:8080/ObstacleAvoidance/ws/'
url_getTrajet = base_url + 'getTrajet'
url_getMap = base_url + 'getMap'
url_getOptimizedMap = base_url + 'getOptimizedMap'
url_getOptimizedTrajet = base_url + 'getOptimizedTrajet'
url_saveMap = base_url + 'saveMap'
url_saveTrajet = base_url + 'saveTrajet'

data = {"eventType": "AAS_PORTAL_START", "data": {"uid": "hfe3hf45huf33545", "aid": "1", "vid": "1"}}
params = {'sessionKey': '9ebbd0b25760557393a43064a92bae539d962103', 'format': 'xml', 'platformId': 1, 'tab' : '[1,2,3,4]'}

r = requests.post(base_url, params=params, data=json.dumps(data), headers=headers)

#r = requests.post(base_url, json={"key": "value"})
#response =  r.json()
#print json.dumps(response)

trajet = []

trajet.append([0,3])
trajet.append([1,3])
trajet.append([2,3])

params = {'trajet': json.dumps(trajet)}

r = requests.post(url_saveTrajet, params=params, headers=headers)

#response =  r.json()
#print json.dumps(response)

lignes = 10
colonnes = 5
mymap = []
for x in range(0, lignes):
	vecteur = []
	for y in range(0, colonnes):
		vecteur.append(1)
	mymap.append(vecteur)

params = {'map': json.dumps(mymap)}

r = requests.post(url_saveMap, params=params, headers=headers)

#response =  r.json()
#print json.dumps(response)

r = requests.post(url_getTrajet, params={}, headers=headers)

response =  r.json()
print response[0]


r = requests.post(url_getMap, params={}, headers=headers)

response =  r.json()
print response[0]
print response[1][1]

