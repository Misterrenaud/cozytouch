#!/usr/bin/python3
__author__ = "Renaud Loiseleux"
__email__ = "renaud.loiseleux@gmail.com"

import requests as requests
from retry import retry

from conf import Conf
from cozytouch.snapshot import Snapshot


class Api:
    URL = "https://ha110-1.overkiz.com/enduser-mobile-web/externalAPI/json/"
    URL_ATLANTIC = "https://apis.groupe-atlantic.com"
    URL_LOGIN = "https://ha110-1.overkiz.com/enduser-mobile-web/enduserAPI"

    class NotAllowedException(Exception):
        pass

    def __init__(self):
        self.session = {}

    def _update_session(self):
        print("update session")
        conf = Conf().get_conf()

        req = requests.post(
            self.URL_ATLANTIC + '/token',
            data={
                'grant_type': 'password',
                'username': 'GA-PRIVATEPERSON/' + conf["cozytouch"]["login"],
                'password': conf["cozytouch"]["password"]
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
        self.session = {"JSESSIONID": jsession.cookies['JSESSIONID']}

    @retry(NotAllowedException, tries=2)
    def _get(self, endpoint: str):
        print(f"GET {endpoint}")
        req = requests.get(
            Api.URL + endpoint,
            headers={
                'cache-control': "no-cache",
                'Host': "ha110-1.overkiz.com",
                'Connection': "Keep-Alive",
            },
            cookies=self.session,
        )
        match req.status_code:
            case 401:
                self._update_session()
                raise Api.NotAllowedException
            case 200:
                return req.json()

    def get_snapshot(self) -> Snapshot:
        return Snapshot(self._get("getSetup"))
