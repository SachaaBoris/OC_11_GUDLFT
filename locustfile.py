# locust -f locustfile.py --headless -u 100 -r 10 -t 30s --host=http://localhost:5000 --html=/locust/report.html
# This locust command will help identify :
#       The load capacity of your application
#       Potential bottlenecks
#       Stability under load
#       Response times under different conditions

from locust import HttpUser, task, between, events
from datetime import datetime
import random


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
            if "Welcome" not in response.text:
                response.failure("Login failed")

    @task(10)
    def view_home(self):
        """View home page."""
        self.client.get("/")

    @task(5)
    def view_board(self):
        """View points board."""
        with self.client.get("/board", catch_response=True) as response:
            if "Club Points Board" not in response.text:
                response.failure("Board page failed to load")

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
            else:
                response.failure("Booking failed")

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

        self.client.post("/purchasePlaces",
                         data={
                             "club": "Simply Lift",
                             "competition": "Spring Festival",
                             **scenario
                         })

# Custom events


@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    print(f"Test started at: {datetime.now()}")


@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    print(f"Test ended at: {datetime.now()}")
