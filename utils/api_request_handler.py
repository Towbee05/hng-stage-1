import httpx
from typing import List
from rest_framework import status
from core.schemas import ApiResult, ApiData, ErrorResponse, AgeResponse, GenderResponse, CountryResponse, CountryProb

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
    
