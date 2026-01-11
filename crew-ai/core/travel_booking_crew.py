from crewai import Crew
from agents.customer_service_agent import CustomerServiceAgent
from agents.travel_advisor_agent import TravelAdvisorAgent
from agents.booking_agent import BookingAgent
from core.crew_tasks import TravelBookingTasks
from config.settings import settings
from typing import Dict, Any, List, Optional
import json


class TravelBookingCrew:

    def __init__(self):
        self.customer_agent = CustomerServiceAgent()
        self.advisor_agent = TravelAdvisorAgent()
        self.booking_agent = BookingAgent()
        self.tasks = TravelBookingTasks()

        self.crew = Crew(
            agents=[
                    self.customer_agent.get_agent(),
                    self.advisor_agent.get_agent(),
                    self.booking_agent.get_agent()
            ],
            tasks=[],
            verbose=settings.verbose,
            max_iterations=settings.max_iterations
        )