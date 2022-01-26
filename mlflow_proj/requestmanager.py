# Author : Bhabesh Chandra Acharya

import json
import requests


# def apiGet(endpoint):
#     return json.loads("{server}{endpoint").format(server=)

class RequestManager:
    _server = None
    _headers = {'content-type': 'application/json'}

    def __init__(self, server):
        self._server = server
        print(self._server)

    def api_get(self, endpoint):
        res = requests.get('{server}{endpoint}'.format(server=self._server, endpoint=endpoint), headers=self._headers)
        return json.loads(res.text)

    def api_post(self, endpoint, body=None):
        res = requests.post('{server}{endpoint}'.format(server=self._server, endpoint=endpoint), headers=self._headers,
                            data=json.dumps(body))
        text = res.text
        if text:
            return json.loads(text)
        else:
            return None

    def api_put(self, endpoint, body=None):
        print(self._server)
        print(endpoint)
        res = requests.put('{server}{endpoint}'.format(server=self._server, endpoint=endpoint), headers=self._headers,
                           data=json.dumps(body))
        text = res.text
        if text:
            return json.loads(text)
        else:
            return None

    def api_delete(self, endpoint):
        return requests.delete('{server}{endpoint}'.format(server=self._server, endpoint=endpoint),
                               headers=self._headers)
