from django.http import JsonResponse, HttpResponse
from django.urls import reverse
from django.db import connection
def db_version(request):
    with connection.cursor() as cursor:
        cursor.execute("SELECT version();")
        version = cursor.fetchone()[0]
    return JsonResponse({'version': version})

def redirect_user(request):
    url = reverse('auth:login')
    return HttpResponse(f'<p> Nothing to see here </p> <p> Login via <a href="{url}"> Login page </a> To fetch github login url. Visit authorization url to get started.')
