import requests


class web_connector:
    def __init__(self) -> None:
        self._session = requests.Session()

    def get(self, url, header={}, param="", redirects=False) -> None:
        return self._session.get(
            url, headers=header, params=param, allow_redirects=redirects
        )

    def getRaw(self, url, header={}, param="", redirects=False) -> None:
        return self._session.get(
            url, headers=header, params=param, allow_redirects=redirects, stream=True
        )

    def post(self, url, data, header="") -> None:
        return self._session.post(url, data, headers=header)

    def put(self, url, data="", header="") -> None:
        return self._session.put(url, data, headers=header)

    def delete(self, url, header="") -> None:
        return self._session.delete(url, headers=header)

    def printCookies(self):
        print(self._session.cookies.get_dict())
