# arquery

import requests
from bs4 import BeautifulSoup
import urllib.parse
import argparse
from getpass import getpass
import pprint

requests.packages.urllib3.disable_warnings()


class arquery:
    def __init__(self) -> None:
        self.session = requests.session()

    def connect(self, school_id, username, password):
        response = self.session.get(
            url=f"https://auhosted4.renlearn.com.au/{school_id}/Public/RPM/Login/Login.aspx?srcID=s",
            verify=False,
        )
        soup = BeautifulSoup(response.text, "html.parser")

        viewstate = soup.find(attrs={"name": "__VIEWSTATE"})["value"]
        viewstategenerator = soup.find(attrs={"name": "__VIEWSTATEGENERATOR"})["value"]
        eventvalidation = soup.find(attrs={"name": "__EVENTVALIDATION"})["value"]

        viewstate = urllib.parse.quote(viewstate)
        viewstategenerator = urllib.parse.quote(viewstategenerator)
        eventvalidation = urllib.parse.quote(eventvalidation)

        """params = {
            "ctl00%24cp_Content%24tbUserName": username,
            "ctl00%24cp_Content%24tbPassword": password,
        }"""

        payload = (
            f"__LASTFOCUS=&__EVENTTARGET=ctl00%24cp_Content%24btnLogIn&__EVENTARGUMENT="
            f"&__VIEWSTATE={viewstate}&__VIEWSTATEGENERATOR={viewstategenerator}&__SCROLLPOSITIONX=0&__SCROLLPOSITIONY=0"
            f"&__VIEWSTATEENCRYPTED=&__EVENTVALIDATION={eventvalidation}&ctl00%24mHeader%24mpreviousID="
            f"&ctl00%24cp_Content%24tbUserName={username}&ctl00%24cp_Content%24tbPassword={password}"
        )

        headers = {"Content-Type": "application/x-www-form-urlencoded"}

        self.session.post(
            url=f"https://auhosted4.renlearn.com.au/{school_id}/Public/RPM/Login/Login.aspx?srcID=s",
            data=payload,
            headers=headers,
            verify=False,
        )

        print(self.session.cookies)


    def get_all_books(self, school_id):

        all_books = []

        response = self.session.get(
            f"https://auhosted4.renlearn.com.au/{school_id}/AR/StudentApp/Bookshelf.aspx"
        )
        soup = BeautifulSoup(response.text, "html.parser")

        all_book_ids = [id.attrs['data-id'] for id in soup.find_all(attrs={"id":"dBook"})]

        soup = BeautifulSoup(response.text, "html.parser")

        viewstate = soup.find(attrs={"name": "__VIEWSTATE"})["value"]
        viewstategenerator = soup.find(attrs={"name": "__VIEWSTATEGENERATOR"})["value"]
        eventvalidation = soup.find(attrs={"name": "__EVENTVALIDATION"})["value"]

        viewstate = urllib.parse.quote(viewstate)
        viewstategenerator = urllib.parse.quote(viewstategenerator)
        eventvalidation = urllib.parse.quote(eventvalidation)

        # Assuming we never need to go above 100!
        for page in range(0,100):
            print(f"Page: {page}")
            payload = (
                f"__LASTFOCUS=&__EVENTTARGET=ctl00%24content%24pnSearchHeader%24mLinkButton_Next&__EVENTARGUMENT="
                f"&__VIEWSTATE={viewstate}&__VIEWSTATEGENERATOR={viewstategenerator}"
                f"&__VIEWSTATEENCRYPTED=&__EVENTVALIDATION={eventvalidation}&ctl00%24mHeader%24mpreviousID="
                f"&ctl00%24content%24pnSearchHeader%24mHiddenPrevNext={page}"
            )

            headers = {"Content-Type": "application/x-www-form-urlencoded"}

            response = self.session.post(
                url=f"https://auhosted4.renlearn.com.au/{school_id}/AR/StudentApp/Bookshelf.aspx",
                data=payload,
                headers=headers,
                verify=False,
            )

            soup = BeautifulSoup(response.text, "html.parser")

            book_ids = [id.attrs['data-id'] for id in soup.find_all(attrs={"id":"dBook"})]

            all_book_ids.extend(book_ids)

            if soup.find('a', attrs={"id": "ctl00_content_pnSearchHeader_mLinkButton_Next"}).get("disabled") == "disabled":
                break
        
        print(len(all_book_ids))

        for book_id in all_book_ids:
            response = self.session.get(url="https://auhosted4.renlearn.com.au/1454662/AR/StudentApp/BookScore.aspx?i=" + book_id)
            soup = BeautifulSoup(response.text, "html.parser")
            title = soup.find(attrs={"id":"ctl00_content_bookDetails_dTitle"}).text
            author = soup.find(attrs={"id":"ctl00_content_bookDetails_dAuthor"}).text
            book_number = soup.find(attrs={"id":"ctl00_content_bookDetails_rptDetails_ctl00_spValue"}).text
            word_count = soup.find(attrs={"id":"ctl00_content_rptScore_ctl02_valueBox_dValue"}).get("text")
            all_books.append({"title": title, "author": author, "book_number": book_number, "word_count": word_count})
            
        return all_books


def main(username, password, school_id):
    url = f"https://auhosted4.renlearn.com.au/{school_id}/Public/RPM/Login/Login.aspx?srcID=s"

    ar = arquery()
    ar.connect(school_id=school_id, username=username, password=password)
    all_books = ar.get_all_books(school_id=school_id)
    pprint.pprint(all_books)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description = 'Query AR bookshelf')
    parser.add_argument('-u', '--username', required=True, type=str)
    parser.add_argument('-p', '--password', required=False, type=str)
    parser.add_argument('-s', '--schoolid', required=True, type=str)

    args = parser.parse_args()

    if not args.password: 
        args.password = getpass()

    main(username=args.username, password=args.password, school_id=args.schoolid)


