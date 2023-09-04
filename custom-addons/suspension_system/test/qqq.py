import requests
import json
	# 000206

url = "http://192.168.20.180:8080/DgApi/Details?StationID=2&WorkLine=车缝五组&ColorNo=1067-WT&BeginTime=2021-12-18&EndTime=2021-12-19&EmpID=000206"
res = requests.get(url)
res.encoding = 'utf-8'
data_list = json.loads(res.text)["Data"]


# print(len(data_list))
# aaa = 0
wdc = {}

for i in data_list:

    if i["SeqNo"] not in wdc:
        wdc[i["SeqNo"]] = [i["Nid"]]
    else:
        wdc[i["SeqNo"]].append(i["Nid"])

for j in wdc:
    print(j, len(wdc[j]))
