from core.schemas import FilterParams
import re

def filter_database(filters: FilterParams, people):
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
    start = (filters.page - 1) * filters.limit
    end = start + filters.limit
    filtered_people = people[start:end]

    return filters, filtered_people


def parse_search_query(q: str) -> FilterParams:
    filter = FilterParams()
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

    if not q is None:
        queries = {
            'gender': [],
            'age_group': None,
            'min_age': None,
            'max_age': None,
        }
        q= q.lower().strip()
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
                filter.gender = None
            else:
                filter.gender = queries['gender'][0]
        if queries['age_group']:
            filter.age_group = queries['age_group']
        if queries['min_age']:
            filter.min_age = queries['min_age']
        if queries['max_age']:
            filter.max_age = queries['max_age']
        # Flag for appropraite filters
        # matched = False
        match_min_age = re.search(r"above (\d+)", q)
        if match_min_age:
            filter.min_age = int(match_min_age.group(1)) + 1

        match_max_age = re.search(r"below (\d+)", q)
        if match_max_age:
            filter.max_age = int(match_max_age.group(1)) - 1

        match_in_country = re.search(r"\b(from|in)\s+([a-z ]+)", q)
        if match_in_country:
            filter.country = match_in_country.group(2).strip()

    return filter
