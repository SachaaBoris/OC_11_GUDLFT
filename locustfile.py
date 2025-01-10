# locust -f locustfile.py --headless -u 6 -r 1 -t 30s --host=http://127.0.0.1:5000 --html=reports/locust/report.html --csv=reports/locust/results
# This locust command will help identify :
#       The load capacity of your application
#       Potential bottlenecks
#       Stability under load
#       Response times under different conditions

from locust import HttpUser, task, between, events
from datetime import datetime
import random


import random
from locust import HttpUser, task, between

class GUDLFTUser(HttpUser):
    wait_time = between(1, 3)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.valid_emails = [
            "john@simplylift.co",
            "admin@irontemple.com",
            "kate@shelifts.co.uk"
        ]
        self.competitions = [
            "Spring Festival",
            "Winter SkiLïft",
            "SummerIs Magic"
        ]

    def on_start(self):
        """Setup initial user state."""
        self.email = random.choice(self.valid_emails)
        # Login
        with self.client.post("/showSummary",
                              data={"email": self.email},
                              catch_response=True) as response:
            if response.status_code != 200:
                response.failure(f"Login failed with status code {response.status_code}")
            elif "Welcome" not in response.text:
                response.failure("Login failed: Unexpected response content")

    @task(10)
    def view_home(self):
        """View home page."""
        with self.client.get("/", catch_response=True) as response:
            if response.status_code != 200:
                response.failure(f"Home page failed with status code {response.status_code}")
            elif "Welcome" not in response.text:
                response.failure("Home page failed: Unexpected response content")

    @task(5)
    def view_board(self):
        """View points board."""
        with self.client.get("/board", catch_response=True) as response:
            if response.status_code != 200:
                response.failure(f"Board page failed with status code {response.status_code}")
            elif "Club Points Board" not in response.text:
                response.failure("Board page failed: Unexpected response content")

    @task(3)
    def book_places(self):
        """Book competition places."""
        competition = random.choice(self.competitions)
        places = random.randint(1, 3)

        with self.client.post("/purchasePlaces",
                              data={
                                  "club": "Simply Lift",
                                  "competition": competition,
                                  "places": str(places)
                              },
                              catch_response=True) as response:
            if "Great-booking complete!" in response.text:
                response.success()
            elif "Not enough points!" in response.text:
                response.failure("Booking failed: Not enough points")
            elif "This competition is no longer bookable." in response.text:
                response.failure("Booking failed: Competition no longer bookable")
            elif "Places to book must be a positive integer." in response.text:
                response.failure("Booking failed: Invalid number of places")
            elif "Clubs are limited to" in response.text:
                response.failure("Booking failed: Booking limit exceeded")
            elif "Competition or club not found!" in response.text:
                response.failure("Booking failed: Competition or club not found")
            else:
                response.failure(f"Unexpected booking response: {response.text}")

    @task(1)
    def invalid_booking(self):
        """Test invalid booking scenarios."""
        scenarios = [
            {"places": "0"},
            {"places": "-1"},
            {"places": "999"},
            {"places": "abc"}
        ]
        scenario = random.choice(scenarios)

        with self.client.post("/purchasePlaces",
                              data={
                                  "club": "Simply Lift",
                                  "competition": "Spring Festival",
                                  **scenario
                              },
                              catch_response=True) as response:
            if "Great-booking complete!" in response.text:
                response.success()
            elif "Not enough points!" in response.text:
                response.failure("Booking failed: Not enough points")
            elif "This competition is no longer bookable." in response.text:
                response.failure("Booking failed: Competition no longer bookable")
            elif "Places to book must be a positive integer." in response.text:
                response.failure("Booking failed: Invalid number of places")
            elif "Clubs are limited to" in response.text:
                response.failure("Booking failed: Booking limit exceeded")
            elif "Competition or club not found!" in response.text:
                response.failure("Booking failed: Competition or club not found")
            else:
                response.failure(f"Unexpected booking response: {response.text}")


# Custom events
@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    print(f"Test started at: {datetime.now()}")


@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    print(f"Test ended at: {datetime.now()}")
