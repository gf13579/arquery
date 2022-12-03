# arquery

import requests
from bs4 import BeautifulSoup
import urllib.parse
import argparse
from getpass import getpass
import pprint
import time
import tempfile
import json
import re
from loguru import logger

requests.packages.urllib3.disable_warnings()


class arquery:
    def __init__(self) -> None:
        self.session = requests.session()

    def connect(self, base_url, school_id, username, password, verify=True):
        response = self.session.get(
            url=f"{base_url}/{school_id}/Public/RPM/Login/Login.aspx?srcID=s",
            verify=verify,
        )
        soup = BeautifulSoup(response.text, "html.parser")

        # Parse all the session info to use for subsequent posts
        viewstate = soup.find(attrs={"name": "__VIEWSTATE"})["value"]
        viewstategenerator = soup.find(attrs={"name": "__VIEWSTATEGENERATOR"})["value"]
        eventvalidation = soup.find(attrs={"name": "__EVENTVALIDATION"})["value"]

        viewstate = urllib.parse.quote(viewstate)
        viewstategenerator = urllib.parse.quote(viewstategenerator)
        eventvalidation = urllib.parse.quote(eventvalidation)

        payload = (
            f"__LASTFOCUS=&__EVENTTARGET=ctl00%24cp_Content%24btnLogIn&__EVENTARGUMENT="
            f"&__VIEWSTATE={viewstate}&__VIEWSTATEGENERATOR={viewstategenerator}&__SCROLLPOSITIONX=0&__SCROLLPOSITIONY=0"
            f"&__VIEWSTATEENCRYPTED=&__EVENTVALIDATION={eventvalidation}&ctl00%24mHeader%24mpreviousID="
            f"&ctl00%24cp_Content%24tbUserName={username}&ctl00%24cp_Content%24tbPassword={password}"
        )

        headers = {"Content-Type": "application/x-www-form-urlencoded"}

        self.session.post(
            url=f"{base_url}/{school_id}/Public/RPM/Login/Login.aspx?srcID=s",
            data=payload,
            headers=headers
        )

        logger.debug(self.session.cookies)


    def get_all_books(self, base_url, school_id):
        all_books = []

        # Get the first page of books
        response = self.session.get(
            f"{base_url}/{school_id}/AR/StudentApp/Bookshelf.aspx"
        )
        soup = BeautifulSoup(response.text, "html.parser")

        all_book_ids = [id.attrs['data-id'] for id in soup.find_all(attrs={"id":"dBook"})]

        soup = BeautifulSoup(response.text, "html.parser")

        # Parse all the session info to use for subsequent posts
        viewstate = soup.find(attrs={"name": "__VIEWSTATE"})["value"]
        viewstategenerator = soup.find(attrs={"name": "__VIEWSTATEGENERATOR"})["value"]
        eventvalidation = soup.find(attrs={"name": "__EVENTVALIDATION"})["value"]

        viewstate = urllib.parse.quote(viewstate)
        viewstategenerator = urllib.parse.quote(viewstategenerator)
        eventvalidation = urllib.parse.quote(eventvalidation)

        # Get all subsequent pages (up to 100)
        for page in range(0,100):
            logger.info(f"Processing page: {page}")
            payload = (
                f"__LASTFOCUS=&__EVENTTARGET=ctl00%24content%24pnSearchHeader%24mLinkButton_Next&__EVENTARGUMENT="
                f"&__VIEWSTATE={viewstate}&__VIEWSTATEGENERATOR={viewstategenerator}"
                f"&__VIEWSTATEENCRYPTED=&__EVENTVALIDATION={eventvalidation}&ctl00%24mHeader%24mpreviousID="
                f"&ctl00%24content%24pnSearchHeader%24mHiddenPrevNext={page}"
            )

            headers = {"Content-Type": "application/x-www-form-urlencoded"}

            response = self.session.post(
                url=f"{base_url}/{school_id}/AR/StudentApp/Bookshelf.aspx",
                data=payload,
                headers=headers,
                verify=False,
            )

            soup = BeautifulSoup(response.text, "html.parser")
            book_ids = [id.attrs['data-id'] for id in soup.find_all(attrs={"id":"dBook"})]
            all_book_ids.extend(book_ids)

            # Exit when we're on the last page  
            if soup.find('a', attrs={"id": "ctl00_content_pnSearchHeader_mLinkButton_Next"}).get("disabled") == "disabled":
                break
        
        logger.info(f"Total book id count: {len(all_book_ids)}")

        b = 0
        for book_id in all_book_ids:
            logger.info(f"Retrieving book {b} - i = {book_id}")
            url = url=f"{base_url}/{school_id}/AR/StudentApp/BookScore.aspx?i=" + book_id
            response = self.session.get(url=url, verify=False, allow_redirects=False)
            logger.debug(str(response.status_code) + " - " + str(len(response.text)) + " - " + url)
            
            # retry up to 5 times, with 5 second pauses
            if response.status_code == 302:
                for i in (1,5):
                    time.sleep(5)
                    response = self.session.get(url=url, verify=False, allow_redirects=False)
                    logger.debug(str(response.status_code) + " - " + str(len(response.text)) + " - " + url)
                    if response.status_code == 200:
                        break
            
            if response.status_code == 302:
                logger.error(f"Failed to fetch {url}")
                time.sleep(5)
                continue

            soup = BeautifulSoup(response.text, "html.parser")
            try:
                title = soup.find(attrs={"id":"ctl00_content_bookDetails_dTitle"}).text
            except Exception as e:
                # This shouldn't happen - we got a response but no reference to the book title
                logger.error(e)

            author = soup.find(attrs={"id":"ctl00_content_bookDetails_dAuthor"}).text.replace("by ","")
            book_number = soup.find(attrs={"id":"ctl00_content_bookDetails_rptDetails_ctl00_spValue"}).text
            # word_count = soup.find(attrs={"id":re.compile("ctl0._content_rptScore_ctl0._valueBox_dValue")})
            word_count = soup.find(attrs={"id":"ctl00_content_rptScore_ctl02_valueBox_dValue"})
            if word_count:
                word_count = word_count.text.replace(",","").replace(" EN","")
            else:
                logger.info(f"No word count for book id {id} - student may not have passed the quiz")

            all_books.append({"title": title, "author": author, "book_number": book_number, "word_count": word_count})
            b += 1
            
        return all_books


def main(base_url, username, password, school_id):
    ar = arquery()
    ar.connect(base_url=base_url, school_id=school_id, username=username, password=password, verify=False)
    all_books = ar.get_all_books(base_url=base_url, school_id=school_id)
    pprint.pprint(all_books)

    temp_file = tempfile.NamedTemporaryFile(delete=False, mode='w+t')
    logger.info(f"Saving to {temp_file.name}")
    temp_file.writelines(json.dumps(all_books))
    temp_file.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description = 'Query AR bookshelf')
    parser.add_argument('-u', '--username', required=True, type=str)
    parser.add_argument('-p', '--password', required=False, type=str)
    parser.add_argument('-s', '--schoolid', required=True, type=str)
    parser.add_argument('-w', '--website', required=True, type=str)

    args = parser.parse_args()

    if not args.password: 
        args.password = getpass()

    main(base_url=args.website, username=args.username, password=args.password, school_id=args.schoolid)


