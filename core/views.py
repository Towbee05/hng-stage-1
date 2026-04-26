import uuid
import asyncio
from ninja import NinjaAPI
from .models import PersonModel
from asgiref.sync import sync_to_async
from .schemas import CreatePersonSchema, SuccessResponse, ErrorResponse, SuccessMultipleResponse
from .utils import fetch_external_api, get_age_group, most_probable_country, errorHandler

api = NinjaAPI()

# Create your views here.
@api.post('', response={200:SuccessResponse, 201: SuccessResponse, 400:ErrorResponse, 408:ErrorResponse, 500: ErrorResponse, 502: ErrorResponse})
async def create_person(request, payload: CreatePersonSchema):
    name = payload.name.strip()
    if not name:
        return 400, errorHandler(400, "Missing or empty name")
    
    person = await PersonModel.objects.filter(name__iexact=name).afirst()
    if person:
        return 200, {
            "status": "success",
            "message": "Profile already exists",
            "data": person
        }
    data: dict[str, str | int | float] = {
        'name': name
    }
    # Fetch from external api
    # fetch gender data
    gender_info, age_info, country_info = await asyncio.gather(
        fetch_external_api('genderize', f'https://api.genderize.io?name={name}'),
        fetch_external_api('agify', f'https://api.agify.io?name={name}'),
        fetch_external_api('nationalize', f'https://api.nationalize.io?name={name}')
    )
    if gender_info.error:
        return gender_info.error.status, errorHandler(gender_info.error.status, gender_info.error.message)
    if gender_info.data:
        gender_data = gender_info.data.gender_data
        if gender_data:
            data['gender'] = gender_data.gender
            data['gender_probability'] = gender_data.probability
            data['sample_size'] = gender_data.count

    # fetch age data
    if age_info.error:
        return age_info.error.status, errorHandler(age_info.error.status, age_info.error.message)
    if age_info.data:
        age_data = age_info.data.age_data
        if age_data:
            data['age'] = age_data.age
            data['age_group'] = get_age_group(int(age_data.age))
    
    # fetch country data
    if country_info.error:
        return country_info.error.status, errorHandler(country_info.error.status, country_info.error.message)
    if country_info.data:
        country_data = country_info.data.country_data
        if country_data:
            prob_country = most_probable_country(country_data.country)
            data['country_id'] = prob_country.country_id
            data['country_probability'] = prob_country.probability

    person = await sync_to_async(PersonModel.objects.create)(**data)
    return 201, {
        "status": "success",
        "data": person
    }

@api.get('', response= {200: SuccessMultipleResponse, 500: ErrorResponse})
async def get_all_profiles(request):
    try: 
        people = await sync_to_async(list)(PersonModel.objects.all())
        return 200, { "status": "success", "count": len(people), "data": people }
    except Exception as e:
        return 500, errorHandler(500, "An unexpected error occurred while fetching the person data")

@api.get('/{id}', response={ 200: SuccessResponse, 404: ErrorResponse, 500: ErrorResponse })
async def get_person(request, id: uuid.UUID):
    try:
        person = await sync_to_async(PersonModel.objects.get)(id=id)
        return 200, {"status": "success", "data": person }
    except PersonModel.DoesNotExist:
        return 404, errorHandler(404, f"No person matching id: '{id}' found")
    except Exception as e:
        return 500, errorHandler(500, "An unexpected error occurred while fetching the person data")
    
@api.delete('/{id}', response={ 204: None, 404: ErrorResponse, 500: ErrorResponse })
async def delete_person(request, id: uuid.UUID):
    try:
        person = await sync_to_async(PersonModel.objects.get)(id=id)
        await sync_to_async(person.delete)()
        # return 204, { "status": "success", "message": f"Person with id: '{id}' has been deleted", "data": person}
        return 204, None
    except PersonModel.DoesNotExist:
        return 404, errorHandler(404, f"No person matching id: '{id}' found")
    except Exception as e:
        return 500, errorHandler(500, "An unexpected error occurred while deleting the person data")