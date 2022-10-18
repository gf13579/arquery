# arquery

import requests
from bs4 import BeautifulSoup
import urllib.parse
import argparse
from getpass import getpass

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
        response = self.session.get(
            f"https://auhosted4.renlearn.com.au/{school_id}/AR/StudentApp/Bookshelf.aspx"
        )
        soup = BeautifulSoup(response.text, "html.parser")

        book_ids = [id.attrs['data-id'] for id in soup.find_all(attrs={"id":"dBook"})]

        print(book_ids)

        # Page through results
        # Gather a list of book IDs e.g. lQLG4WTBzgxme8CXQ9JczQ%3d%3d
        # Then hit https://auhosted4.renlearn.com.au/1454662/AR/StudentApp/BookScore.aspx?i= for each one

        """
        The relevant paramter is ctl00%24content%24pnSearchHeader%24mHiddenPrevNext=3

        We're done when the content contains id="ctl00_content_pnSearchHeader_mLinkButton_Next" disabled="disabled"

        full:
        ctl00%24content%24pnSearchHeader%24mText_searchFilter=&ctl00%24content%24pnSearchHeader%24ScrollPos=0&ctl00%24content%24pnSearchHeader%24mHiddenPrevNext=3&ctl00%24content%24pnFooter%24mHiddenPrevNext=&ctl00%24hClass=94%3B2%3BDavis
        """


def main(username, password, school_id):
    url = f"https://auhosted4.renlearn.com.au/{school_id}/Public/RPM/Login/Login.aspx?srcID=s"

    ar = arquery()
    ar.connect(school_id=school_id, username=username, password=password)
    ar.get_all_books(school_id=school_id)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description = 'Query AR bookshelf')
    parser.add_argument('-u', '--username', required=True, type=str)
    parser.add_argument('-p', '--password', required=False, type=str)
    parser.add_argument('-s', '--schoolid', required=True, type=str)

    args = parser.parse_args()

    if not args.password: 
        args.password = getpass()

    main(username=args.username, password=args.password, school_id=args.schoolid)


# Dumping ground for notes - content I need to parse

"""

POST /1454662/AR/StudentApp/Bookshelf.aspx

<div id="dBook" class="book" data-id="DlaZWufmZtP27IKE78Lmwg%3d%3d">
    <img src="https://z14resources.renlearnrp.com/bookimageservice/300219/EN/RP/tmb" id="ctl00_content_rptMonths_ctl00_rptBooks_ctl08_iBook" style="width:100%; height:auto;" /><br />
    <div id="ctl00_content_rptMonths_ctl00_rptBooks_ctl08_dScore" class="smallBox roundedCornersSm" style="display:inline-block; margin:10px 0px; padding:2px 2px; width:5em;">90%</div>
    <div id="ctl00_content_rptMonths_ctl00_rptBooks_ctl08_dDetails" style="white-space:nowrap; font-size:90%; padding:6px;">&nbsp;</div>
    
</div>

https://auhosted4.renlearn.com.au/1454662/AR/StudentApp/BookScore.aspx?i=lVEc4WBkT0lCw9DqUZNAvg%3d%3d

	<div id="ctl00_content_bookDetails_dTitle" style="font-weight:bold;">These Happy Golden Years</div>
	<div id="ctl00_content_bookDetails_dAuthor">by Laura Ingalls Wilder</div>


"""
