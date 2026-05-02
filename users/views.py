from django.shortcuts import redirect
from ninja import NinjaAPI, Query
from utils.pcke_generator import generate_pcke
from django.conf import settings
from django.contrib.auth import get_user_model
from ninja_jwt.tokens import RefreshToken
from .schema import TokenRefreshInputSchema, TokenPairOutputSchema, TokenPairOutputResponseSchema
from core.schemas import ErrorResponse
from utils.errorHandler import errorHandler
import requests
import secrets
# Create your views here.

api = NinjaAPI()
User = get_user_model()
# load_dotenv()
@api.get('/github')
def github_login(request):
    # Redirect users to the github login page
    code_verifier, code_hash = generate_pcke()
    print(code_verifier)
    state = secrets.token_urlsafe(16)
    request.session[f'pcke_{state}'] = code_verifier 
    client_ID = settings.GITHUB_CLIENT_ID
    callback_url='http://localhost:8000/auth/github/callback'
    url = f'https://github.com/login/oauth/authorize?client_id={client_ID}&redirect_uri={callback_url}&code_challenge={code_hash}&code_challenge_method=S256&state={state}'
    return redirect(url)

@api.get('/github/callback', response={ 200: dict, 400: dict, 500: dict })
def github_login_callback(request, code: str, state: str):
    try:
        # Handles the callback from github after user has authenticated
        code_verifier = request.session.get(f'pcke_{state}')
        print(code_verifier)
        data = get_access_token(code, code_verifier)
        if data.get('error'):
            return 400, { 'success': False, 'message': data.get('error_description') }
        
        user_info = get_user_details(access_token=data.get('access_token'))
        username = user_info.get('login')
        avatar_url = user_info.get('avatar_url')
        github_id = user_info.get('id')
        email = user_info.get('email') if not user_info.get('email') is None else f"{github_id}@github.local"

        user = User.objects.filter(github_id=github_id).first()
        if not user and email:
            user = User.objects.filter(email=email).first()
        if user:
            user.github_id= github_id
            user.username= username
            user.avatar_url = avatar_url
        else:
            user= User.objects.create(github_id=github_id, email=email, username=username, avatar_url=avatar_url )
            user.set_unusable_password()
            user.save()
        
        token = create_user_access_token(user)

        return 200, { 'data': token }
    except Exception as e:
        return 500, { 'success': False, 'message': 'An error occurred!!' }

@api.post('/refresh', response={ 200: TokenPairOutputResponseSchema, 404: ErrorResponse, 500: ErrorResponse })
def refresh_access_token(request, payload: TokenRefreshInputSchema):
    try:
        if not payload.refresh_token:
            return 404, errorHandler(404, 'Please provide refresh token')

        refresh = RefreshToken(payload.refresh_token)
        return 200, TokenPairOutputResponseSchema(status='success', data=TokenPairOutputSchema(access_token=str(refresh.access_token), refresh_token=str(refresh)))
    except Exception as e:
        return 500, errorHandler(500, 'An error occurred while creating access token')

def create_user_access_token(user) -> TokenPairOutputSchema:
    # Implementation for creating user access token
    refresh = RefreshToken.for_user(user)
    return TokenPairOutputSchema(access_token=str(refresh.access_token), refresh_token=str(refresh))
    

def get_access_token(code, code_verifier):
    response = requests.post(
        'https://github.com/login/oauth/access_token', 
        headers= { 'Accept': 'application/json' },
        data= {
            'client_id': settings.GITHUB_CLIENT_ID,
            'client_secret': settings.GITHUB_CLIENT_SECRET,
            'code': code, 
            'code_verifier': code_verifier
        })
    print(response.json())
    data = response.json()
    return data

def get_user_details(access_token: str):
    response = requests.get('https://api.github.com/user', headers={ 
        "Authorization": f"Bearer {access_token}",  
        "Accept": "application/json"
        })
    return response.json()