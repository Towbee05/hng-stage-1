import httpx
from typing import List
from rest_framework import status
from .schemas import ApiResult, ApiData, ErrorResponse, AgeResponse, GenderResponse, CountryResponse, CountryProb
import re

# Fetch external api based on params
async def fetch_external_api(api_name: str, url: str) -> ApiResult:
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, timeout=10)
            if response.status_code != 200:
                return ApiResult(success=False, data=None, error=ErrorResponse(status=response.status_code, message=f"{api_name} API returned an invalid response"))
            data = response.json()
            if not data or not data.get('count'):
                return ApiResult(success=False, data=None, error=ErrorResponse(status=status.HTTP_502_BAD_GATEWAY, message=f"{api_name} API returned an invalid response"))
            if api_name == "agify":
                return ApiResult(success=True, data=ApiData(age_data=AgeResponse(count=data['count'], age=data['age']), gender_data=None, country_data=None), error=None)
            elif api_name == "genderize":
                return ApiResult(success=True, data=ApiData(age_data=None, gender_data= GenderResponse(count=data['count'], gender=data['gender'], probability=data['probability']), country_data=None), error=None)
            elif api_name == "nationalize":
                return ApiResult(success=True, data=ApiData(age_data=None, gender_data= None, country_data=CountryResponse(count=data['count'], country=data['country'])), error=None)
            else: 
                return ApiResult(success=False, data=None, error=ErrorResponse(status=status.HTTP_500_INTERNAL_SERVER_ERROR, message="An error occurred.  Please cross check API endpoints, if problem persists contact administrator"))
    except httpx.TimeoutException:
        return ApiResult(success=False, data=None, error=ErrorResponse(status=status.HTTP_408_REQUEST_TIMEOUT, message=f"{api_name} API timed out"))
    except httpx.HTTPError:
        return ApiResult(success=False, data=None, error=ErrorResponse(status=status.HTTP_500_INTERNAL_SERVER_ERROR, message=f"Error occurred while trying to access {api_name} api"))

# Get age group based on given age
def get_age_group(age: int) -> str:
    if age <= 12:
        return "child"
    elif (age >= 13) and (age <= 19):
        return "teenager"
    elif (age >= 20) and (age <= 59):
        return "adult"
    else:
        return "senior"
    
# Get the country with the highest probability
def most_probable_country(arr: List[CountryProb]) -> CountryProb:
    return max(arr, key=lambda x:x.probability)
    
# Helper function to handle all error responses
def errorHandler(status:int, message:str) -> ErrorResponse:
    return ErrorResponse(
        status= status,
        message= message
    )

def parse_search_query(q: str, filters):
    gender_query_map = {
        'male': 'male',
        'males': 'male',
        'female': 'female',
        'females': 'female',
    }
    agegroup_query_map = {
        'young': {
            'min_age': 16,
            'max_age': 24
        },
        'child': 'child',
        'children': 'child',
        'teenager': 'teenager',
        'teenagers': 'teenager',
        'adult': 'adult',
        'adults': 'adult',
        'senior': 'senior',
        'seniors': 'senior'
    }

    if not filters.q is None:
        queries = {
            'gender': [],
            'age_group': None,
            'min_age': None,
            'max_age': None,
        }
        q= filters.q.lower().strip()
        q_arr = q.split()
        for i in q_arr:
            if i in gender_query_map.keys():
                queries['gender'].append(gender_query_map[i])
            if i in agegroup_query_map.keys():
                if i == 'young':
                    queries['min_age'] = agegroup_query_map[i]['min_age']
                    queries['max_age'] = agegroup_query_map[i]['max_age']
                else:
                    queries['age_group'] = agegroup_query_map[i]
        # Watch for patterns in queries
        # Check if certain age range was requested for
        if queries['gender']:
            if len(queries['gender']) > 1:
                filters.gender = None
            else:
                filters.gender = queries['gender'][0]
        if queries['age_group']:
            filters.age_group = queries['age_group']
        if queries['min_age']:
            filters.min_age = queries['min_age']
        if queries['max_age']:
            filters.max_age = queries['max_age']
        match = re.search(r"above (\d+)", q)
        print(match)
        if match:
            # queries['min_age'] = match.group(1)
            filters.min_age = int(match.group(1)) + 1
        match = re.search(r"below (\d+)", q)
        print(match)
        if match:
            filters.max_age = int(match.group(1)) - 1
        match = re.search(r"from ([a-z ]+)", q)
        print(match)
        if match:
            filters.country = match.group(1).strip()