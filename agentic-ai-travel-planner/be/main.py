import logging
import os

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from langchain_groq import ChatGroq

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

f_obj = FastAPI(title="AI Travel Planner API", version="1.0.0")

MODEL_NAME = os.getenv("GROQ_MODEL", "openai/gpt-oss-20b")


class TripRequest(BaseModel):
    starting_loc: str = Field(min_length=1, max_length=120)
    destination_loc: str = Field(min_length=1, max_length=120)
    no_of_trip_dys: int = Field(ge=1, le=60)
    no_of_people: int = Field(ge=1, le=30)
    budget: float = Field(gt=0)
    specifications: str = Field(default="", max_length=2000)


@f_obj.get("/")
def root():
    return {"message": "AI Travel Planner API is running", "docs": "/docs"}


@f_obj.get("/health")
def health():
    return {"status": "ok"}


def get_llm():
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise HTTPException(
            status_code=500,
            detail="GROQ_API_KEY is not configured on the backend."
        )

    return ChatGroq(
        model=MODEL_NAME,
        api_key=api_key,
        temperature=0.2,
    )


@f_obj.post("/plan_trip")
def plan_the_trip(payload: TripRequest):
    prompt = f"""
You are an AI Travel Planning Agent.

Create a personalized, practical, budget-aware travel plan using the details below.

Your objectives:
1. Plan the journey from the starting location to the destination.
2. Suggest suitable transportation options and estimated costs.
3. Suggest accommodation appropriate for the budget.
4. Create a realistic day-by-day itinerary.
5. Recommend attractions and activities.
6. Estimate food, transportation, accommodation, activities and miscellaneous costs.
7. Provide a total estimated trip cost and compare it with the user's budget.
8. If the budget is insufficient, suggest ways to reduce costs.
9. Avoid unrealistic schedules and allow reasonable travel time.
10. Clearly label prices as estimates. Do not pretend to have live booking prices.

Trip details:
Starting Location: {payload.starting_loc}
Destination Location: {payload.destination_loc}
Number of Trip Days: {payload.no_of_trip_dys}
Number of People: {payload.no_of_people}
Total Budget: {payload.budget}
Special Specifications: {payload.specifications or "No additional specifications"}

Use this structure:

## 1. Trip Overview
- Starting location
- Destination
- Number of days and people
- Total budget
- Travel style

## 2. Transportation Plan
- Recommended transportation
- Estimated travel time and cost
- Local transportation options and estimated cost

## 3. Accommodation Plan
- Recommended type and area
- Estimated cost per night
- Total accommodation cost
- Reason for recommendation

## 4. Day-by-Day Itinerary
For each day include morning, afternoon, evening, places, activities and estimated costs.

## 5. Food Plan
Recommend local cuisine and budget-friendly food options. Estimate daily food costs.

## 6. Budget Breakdown
Transportation:
Accommodation:
Food:
Activities:
Local Travel:
Miscellaneous:
Total Estimated Cost:
Remaining Budget or Amount Over Budget:

## 7. Budget Optimization
Suggest cheaper alternatives if needed.

## 8. Important Travel Tips
Include season, transport, safety, local customs and booking tips.

## 9. Final Recommendation
Explain whether the trip is practical within the budget.

Important:
- Keep the itinerary realistic.
- Respect the number of people, trip duration, budget and specifications.
- State assumptions when information is missing.
- Do not invent exact prices or claim live availability.
- Return a clean, structured answer.
"""

    try:
        response = get_llm().invoke(prompt)
        return {"content": response.content}
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Travel plan generation failed")
        raise HTTPException(
            status_code=502,
            detail="The AI service could not generate the travel plan. Check the backend logs and Groq quota."
        ) from exc
