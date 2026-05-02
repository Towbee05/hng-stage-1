import re

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