"""RCTBC Web Scraper."""

from datetime import datetime

from bs4 import BeautifulSoup
import requests


class Rctbc:
    """Handle requests to RCTBC Website."""

    def __init__(self, number, postcode):
        """Initialize class."""
        self.number = number
        self.postcode = postcode
        self.data = {
            "recycling": "Unknown",
            "waste": "Unknown",
            "calcol": "Unknown",
            "wasteDate": "Unknown",
            "nextCollection": "Unknown",
        }

    def update(self):
        """Get the latest data from RCTBC."""
        url = (
            "https://www.rctcbc.gov.uk/EN/Resident/BinsandRecycling/"
            "BinCollectionDays.aspx?PropertyNumber="
            + self.number
            + "&Postcode="
            + self.postcode
        )

        session = requests.Session()
        request = session.get(url)

        if request.status_code == 200:
            soup = BeautifulSoup(request.text, "html.parser")
            data = soup.findAll("strong")

            if len(data) == 0:
                return

            next_collection = ""

            start_time = datetime.strptime(data[1].text.split(" ")[1], "%d/%m/%Y")
            start_time = start_time.timestamp() - 604800

            end_time = datetime.strptime(data[1].text.split(" ")[1], "%d/%m/%Y")
            end_time = end_time.timestamp()

            now = datetime.now().timestamp()

            if now > start_time and now < end_time:
                next_collection = "All Bins"
            else:
                next_collection = "Recycling"

            self.data = {
                "recycling": data[0].text,
                "waste": data[1].text.split(" ")[0],
                "calcol": data[2].text.capitalize(),
                "wasteDate": data[1].text.split(" ")[1],
                "nextCollection": next_collection,
            }
