import uuid
import asyncio
from ninja import NinjaAPI, Query
from .models import PersonModel
from asgiref.sync import sync_to_async
from .schemas import CreatePersonSchema, SuccessResponse, ErrorResponse, SuccessMultipleResponse, FilterParams
from utils.errorHandler import errorHandler
from utils.query_parser import parse_search_query
from utils.api_request_handler import fetch_external_api, most_probable_country, get_age_group
import re
api = NinjaAPI()

# Create your views here.
# @api.post('', response={200:SuccessResponse, 201: SuccessResponse, 400:ErrorResponse, 408:ErrorResponse, 500: ErrorResponse, 502: ErrorResponse})
# async def create_person(request, payload: CreatePersonSchema):
#     name = payload.name.strip()
#     if not name:
#         return 400, errorHandler(400, "Missing or empty name")
    
#     person = await PersonModel.objects.filter(name__iexact=name).afirst()
#     if person:
#         return 200, {
#             "status": "success",
#             "message": "Profile already exists",
#             "data": person
#         }
#     data: dict[str, str | int | float] = {
#         'name': name
#     }
#     # Fetch from external api
#     # fetch gender data
#     gender_info, age_info, country_info = await asyncio.gather(
#         fetch_external_api('genderize', f'https://api.genderize.io?name={name}'),
#         fetch_external_api('agify', f'https://api.agify.io?name={name}'),
#         fetch_external_api('nationalize', f'https://api.nationalize.io?name={name}')
#     )
#     if gender_info.error:
#         return gender_info.error.status, errorHandler(gender_info.error.status, gender_info.error.message)
#     if gender_info.data:
#         gender_data = gender_info.data.gender_data
#         if gender_data:
#             data['gender'] = gender_data.gender
#             data['gender_probability'] = gender_data.probability
#             data['sample_size'] = gender_data.count

#     # fetch age data
#     if age_info.error:
#         return age_info.error.status, errorHandler(age_info.error.status, age_info.error.message)
#     if age_info.data:
#         age_data = age_info.data.age_data
#         if age_data:
#             data['age'] = age_data.age
#             data['age_group'] = get_age_group(int(age_data.age))
    
#     # fetch country data
#     if country_info.error:
#         return country_info.error.status, errorHandler(country_info.error.status, country_info.error.message)
#     if country_info.data:
#         country_data = country_info.data.country_data
#         if country_data:
#             prob_country = most_probable_country(country_data.country)
#             data['country_id'] = prob_country.country_id
#             data['country_probability'] = prob_country.probability

#     person = await sync_to_async(PersonModel.objects.create)(**data)
#     return 201, {
#         "status": "success",
#         "data": person
#     }

@api.get('', response= {200: SuccessMultipleResponse, 422: ErrorResponse, 500: ErrorResponse})
def get_all_profiles(request, filters: FilterParams= Query(...)):
    try: 
        people = PersonModel.objects.all()
        if filters.q:
            parse_search_query(filters.q, filters)
        if not filters.gender is None:
            people= people.filter(gender__iexact=filters.gender)
        if not filters.age_group is None:
            people = people.filter(age_group__iexact=filters.age_group)
        if not filters.country_id is None:
            people = people.filter(country_id__iexact=filters.country_id)
        if not filters.country is None:
            people = people.filter(country_name__iexact=filters.country)
        if not filters.min_age is None:
            people = people.filter(age__gte=filters.min_age)
        if not filters.max_age is None:
            people = people.filter(age__lte=filters.max_age)
        if not filters.min_gender_probability is None:
            people = people.filter(gender_probability__gte=filters.min_gender_probability)
        if not filters.min_country_probability is None:
            people = people.filter(country_probability__gte=filters.min_country_probability)
        if not filters.sort_by is None:
            if not filters.order is None:
                if filters.order == "asc":
                    people = people.order_by(filters.sort_by)
                elif filters.order == "desc":
                    people = people.order_by(f"-{filters.sort_by}")
                else:
                    people = people.order_by(filters.sort_by)
            else:
                people=people.order_by("?")
        limit = 10 if filters.limit is None else int(filters.limit)
        if limit > 50:
            return 422, errorHandler(422, "Invalid query parameters")
        page = 1 if filters.page is None else int(filters.page)
        if page < 1:
            return 422, errorHandler(422, "Invalid query parameters")
        start = (page - 1) * limit
        end = start + limit
        print(f"[{start}: {end}]")
        people = people[start:end]
        print(filters)
        return 200, { "status": "success", "page": page, "count": len(people), "data": people }
    except Exception as e:
        raise e
        return 500, errorHandler(500, "An unexpected error occurred while fetching the person data")

@api.get('/{id}', response={ 200: SuccessResponse, 404: ErrorResponse, 500: ErrorResponse })
async def get_person(request, id: uuid.UUID):
    try:
        person = await sync_to_async(PersonModel.objects.get)(id=id)
        return 200, {"status": "success", "data": person }
    except PersonModel.DoesNotExist:
        return 404, errorHandler(404, f"No person matching id: '{id}' found")
    except Exception as e:
        print(e)
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
        print(e)
        return 500, errorHandler(500, "An unexpected error occurred while deleting the person data")
