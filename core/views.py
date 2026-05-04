from .schemas import CreatePersonSchema, SuccessResponse, ErrorResponse, SuccessMultipleResponse, FilterParams, LinksSchema
from utils.api_request_handler import fetch_external_api, most_probable_country, get_age_group
from utils.query_parser import parse_search_query, filter_database
from ninja.throttling import AuthRateThrottle, AnonRateThrottle
from django.http import HttpResponse, StreamingHttpResponse
from utils.errorHandler import errorHandler
from utils.generateTempFile import generate_temp_file
from ninja import NinjaAPI, Query, Header
from datetime import timezone, datetime
from asgiref.sync import sync_to_async
from utils.get_links import get_links
from users.views import AuthBearer
from .models import PersonModel
import tempfile
import uuid
import asyncio
import re
import io
import json
import csv

api = NinjaAPI(throttle=[AnonRateThrottle("60/m"), AuthRateThrottle("60/m")])
# Create your views here.
@api.post('', auth=AuthBearer(), response={
    200:SuccessResponse, 201: SuccessResponse,
    400:ErrorResponse, 401: ErrorResponse,
    403: ErrorResponse, 408:ErrorResponse,
    500: ErrorResponse, 502: ErrorResponse
    })
async def create_person(request, payload: CreatePersonSchema, api_version: str | None = Header(alias='X-API-Version', default=None)):
    if api_version is None:
        return 400, errorHandler(status=400, message="API version header required")
    user = request.auth
    if user is None:
        return 401, errorHandler(401, "Please provide valid access token to access resources")
    if not user.is_admin:
        return 403, errorHandler(401, "Unauthorized entry")

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
            # data['sample_size'] = gender_data.count

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

@api.get('', auth=AuthBearer(), response= {200: SuccessMultipleResponse, 400: ErrorResponse, 422: ErrorResponse, 500: ErrorResponse})
def get_all_profiles(request, filters: FilterParams= Query(...), api_version: str | None = Header(alias="X-API-Version", default=None)):
    try:
        if api_version is None:
            return 400, errorHandler(status=400, message="API version header required")
        user = request.auth
        people = PersonModel.objects.all()

        applied_filter, people = filter_database(filters, people)
        limit, page = applied_filter.limit, applied_filter.page

        if limit > 50:
            return 422, errorHandler(422, "Invalid query parameters")
        if page < 1:
            return 422, errorHandler(422, "Invalid query parameters")

        start = (page - 1) * limit
        end = start + limit
        filtered_people = people[start:end]
        total = people.count()
        total_pages = round(total / limit)

        # Computing current link, next, and previos links
        prev, next, curr = get_links(page, limit, total_pages)
        return 200, {
            "status": "success",
            "page": page,
            "limit": limit,
            "total": total,
            "total_pages": total_pages,
            "links": LinksSchema(self=curr, next=next, prev=prev),
            "data": filtered_people
        }
    except Exception as e:
        # raise e
        return 500, errorHandler(500, "An unexpected error occurred while fetching the person data")

@api.get('/search', auth=AuthBearer(), response={ 200:SuccessMultipleResponse, 400: ErrorResponse, 500: ErrorResponse })
def search_database(request, q: str | None = None, api_version: str | None= Header(alias='X-API-Version', default=None)):
    try:
        if api_version is None:
            return 400, errorHandler(status=400, message="API version header required")
        if q is None or q.strip() == '':
            return 400, errorHandler(400, "Please enter search value")
        filters = parse_search_query(q)

        applied_filter, filtered_people = filter_database(filters, PersonModel.objects.all())
        limit, page = applied_filter.limit, applied_filter.page

        if limit > 50:
            return 422, errorHandler(422, "Invalid query parameters")
        if page < 1:
            return 422, errorHandler(422, "Invalid query parameters")

        total = PersonModel.objects.count()
        total_pages = round(total / limit)
        # Computing current link, next, and previos links
        prev, next, curr = get_links(page, limit, total_pages)
        return 200, {
            "status": "success",
            "page": page,
            "limit": limit,
            "total": total,
            "total_pages": total_pages,
            "links": LinksSchema(self=curr, next=next, prev=prev), "data": filtered_people
        }

    except Exception as e:
        print(e)
        return 500, errorHandler(500, "An unexpected error occurred while fetching the person data")

@api.get('/export', auth=AuthBearer(), response={ 400: ErrorResponse, 422: ErrorResponse})
def export_data(request, format: str | None = None, filters: FilterParams=Query(...) ,api_version: str | None = Header(alias="X-API-Version", default=None)):
    if api_version is None:
        return 400, errorHandler(400, "API version header required")

    if format is None:
        return 400, errorHandler(400, "Please select format to export: (csv, pdf, json)")

    if not format in ['csv', 'pdf', 'json']:
        return 400, errorHandler(400, "Unsupported format. Format must be one of ('csv', 'pdf', 'json')")

    applied_filter, people = filter_database(filters, PersonModel.objects.all())

    if applied_filter.limit > 50:
        return 422, errorHandler(422, "Invalid query parameters")
    if applied_filter.page < 1:
        return 422, errorHandler(422, "Invalid query parameters")

    columns = ["id", "name", "gender", "gender_probability", "age", "age_group", "country_id", "country_name", "country_probability", "created_at"]
    if format == 'csv':
        # Create an in-memory storage location to hold csv content
        output = io.StringIO()
        # Write into the in-memory storage
        writer = csv.DictWriter(output, fieldnames=columns)
        # Write first row (header)
        writer.writeheader()
        timestamp = datetime.utcnow().strftime("%Y%m%d-%H%M%S")
        writer.writerows(people.values(*columns))
        response = HttpResponse(output.getvalue(), content_type='text/csv')
        response['Content-Disposition']= f"attachment; filename=profiles_{timestamp}.csv"
        return response
    if format == 'pdf':
        temp = generate_temp_file(people)
        response = StreamingHttpResponse(temp, content_type= 'application/pdf')
        timestamp = datetime.utcnow().strftime("%Y%m%d-%H%M%S")
        response['Content-Disposition'] = f"attachment; filename=profiles_{timestamp}.pdf"
        return response

    if format == "json":
        response = HttpResponse(json.dumps(list(people.values(*columns)), indent=4, default=str), content_type= 'application/json')
        timestamp = datetime.utcnow().strftime("%Y%m%d-%H%M%S")
        response['Content-Disposition'] = f"attachment; filename=profiles_{timestamp}.json"
        return response

@api.get('/{id}', auth=AuthBearer(), response={ 200: SuccessResponse, 404: ErrorResponse, 500: ErrorResponse })
async def get_person(request, id: uuid.UUID, api_version: str | None = Header(alias='X-API-Version', default=None)):
    try:
        if api_version is None:
            return 400, errorHandler(status=400, message="API version header required")

        person = await sync_to_async(PersonModel.objects.get)(id=id)
        return 200, {"status": "success", "data": person }
    except PersonModel.DoesNotExist:
        return 404, errorHandler(404, f"No person matching id: '{id}' found")
    except Exception as e:
        print(e)
        return 500, errorHandler(500, "An unexpected error occurred while fetching the person data")

@api.delete('/{id}', auth=AuthBearer(), response={ 204: None, 404: ErrorResponse, 500: ErrorResponse })
async def delete_person(request, id: uuid.UUID, api_version: str | None = Header(alias='X-API-Version', default=None)):
    user = request.auth
    if not user.is_admin:
        return 403, errorHandler(401, "Unauthorized entry")
    if api_version is None:
        return 400, errorHandler(status=400, message="API version header required")

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
