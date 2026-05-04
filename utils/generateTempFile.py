from reportlab.lib import colors
from reportlab.lib.pagesizes import landscape, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle

import tempfile

def generate_temp_file(people):
    columns = [
        "id", "name", "gender", "gender_probability", "age", "age_group", "country_id", "country_name", "country_probability", "created_at"
    ]
    temp = tempfile.NamedTemporaryFile(delete=False)
    doc = SimpleDocTemplate(temp.name, pagesize=landscape(A4))
    data = [ columns ]
    for person in people:
        data.append([
            str(person.id), person.name, person.gender,
            person.gender_probability, person.age,
            person.age_group, person.country_id, person.country_name, person.country_probability, person.created_at
        ])
    table = Table(data)
    table.setStyle(TableStyle([
        ("GRID", (0,0), (-1,-1), 1, colors.black),
        ("FONTSIZE", (0,0), (-1,-1), 7),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, 0), 8),
    ]))
    doc.build([table])
    temp.seek(0)
    return temp
