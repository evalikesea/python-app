import requests
import urllib3
from lxml import etree
from config import USER_NAME_GH, PASSWORD_GH

urllib3.disable_warnings()

class GithubLogin(object):
    def __init__(self):
        self.session = requests.session()
        self.session.verify = False
        self.session.headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36"
        }

    def get_params(self):
        url = r"https://github.com/login"
        resp = self.session.get(url)
        selector = etree.HTML(resp.text)
        authenticity_token = selector.xpath('//input[@name="authenticity_token"]/@value')[0]
        timestamp = selector.xpath('//input[@name="timestamp"]/@value')[0]
        timestamp_secret = selector.xpath('//input[@name="timestamp_secret"]/@value')[0]
        return authenticity_token, timestamp, timestamp_secret

    def login(self):
        authenticity_token, timestamp, timestamp_secret = self.get_params()
        data = {
            "authenticity_token": authenticity_token,
            "ga_id": "",
            "login": USER_NAME_GH,
            "password": PASSWORD_GH,
            "webauthn-support": "unknown",
            "webauthn-iuvpaa-support": "unknown",
            "return_to": "",
            "required_field_7d22": "",
            "timestamp": timestamp,
            "timestamp_secret": timestamp_secret,
            "commit": "Sign in"
        }
        post_url = r"https://github.com/session"
        resp = self.session.post(post_url, data=data)
        if resp.status_code == 200:
            print("success")

if __name__ == "__main__":
    githubLogin = GithubLogin()
    githubLogin.login()
