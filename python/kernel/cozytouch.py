#!/usr/bin/python3
__author__ = "Renaud Loiseleux"
__email__ = "renaud.loiseleux@gmail.com"

import requests as requests
from retry import retry

from kernel.storage import Storage


class Cozytouch:
    URL = "https://ha110-1.overkiz.com/enduser-mobile-web/externalAPI/json/"
    URL_ATLANTIC = "https://apis.groupe-atlantic.com"
    URL_LOGIN = "https://ha110-1.overkiz.com/enduser-mobile-web/enduserAPI"

    class NotAllowedException(Exception):
        pass

    def __init__(self, conf):
        self.conf = conf

    def _update_session(self):
        print("update session")
        req = requests.post(
            self.URL_ATLANTIC + '/token',
            data={
                'grant_type': 'password',
                'username': 'GA-PRIVATEPERSON/' + self.conf["cozytouch"]["login"],
                'password': self.conf["cozytouch"]["password"]
            },
            headers={
                'Content-Type': 'application/x-www-form-urlencoded',
                'Authorization': 'Basic Q3RfMUpWeVRtSUxYOEllZkE3YVVOQmpGblpVYToyRWNORHpfZHkzNDJVSnFvMlo3cFNKTnZVdjBh'
            }
        )
        atlantic_token = req.json()['access_token']
        reqjwt = requests.get(
            self.URL_ATLANTIC + '/magellan/accounts/jwt',
            headers={
                'Authorization': 'Bearer ' + atlantic_token + ''
            }
        )
        jsession = requests.post(
            self.URL_LOGIN + '/login',
            data={
                'jwt': reqjwt.content.decode().replace('"', '')
            }
        )
        Storage().set("session_obj", {"JSESSIONID": jsession.cookies['JSESSIONID']})

    @retry(NotAllowedException, tries=2)
    def _get(self, endpoint: str):
        print(f"GET {endpoint}")
        req = requests.get(
            Cozytouch.URL + endpoint,
            headers={
                'cache-control': "no-cache",
                'Host': "ha110-1.overkiz.com",
                'Connection': "Keep-Alive",
            },
            cookies=Storage().get('session_obj', {})
        )
        match req.status_code:
            case 401:
                self._update_session()
                raise Cozytouch.NotAllowedException
            case 200:
                return req.json()

    def get_state(self):
        return self._get("getSetup")