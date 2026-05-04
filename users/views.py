from .schema import TokenRefreshInputSchema, TokenPairOutputSchema, TokenPairOutputResponseSchema, PassToClientSchema
from ninja.throttling import AuthRateThrottle, AnonRateThrottle
from utils.pcke_generator import generate_pcke
from django.contrib.auth import get_user_model
from utils.errorHandler import errorHandler
from ninja_jwt.tokens import RefreshToken
from datetime import datetime, timedelta
from core.schemas import ErrorResponse
from ninja.security import HttpBearer
from django.shortcuts import redirect
from django.core.cache import cache
from django.conf import settings
from ninja import NinjaAPI, Query
import requests
import secrets
import uuid
import jwt
# Create your views here.

api = NinjaAPI(
    throttle=[
        AnonRateThrottle("10/m"),
        AuthRateThrottle("10/m")
    ]
)
User = get_user_model()
# load_dotenv()

# authenticate user logic
class AuthBearer(HttpBearer):
    def authenticate(self, request, token):
        try:
            payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_SECRET_ALGORITHM])
            print(payload)
            if payload['type'] != 'access':
                return None
            user = User.objects.get(id=uuid.UUID(payload['user_id']))
            print(user)
            return user
        except jwt.ExpiredSignatureError:
            return None
        except (jwt.InvalidTokenError, User.DoesNotExist):
            return None
        except Exception as e:
            print(e)
            return None

@api.get('/github', response={200: PassToClientSchema})
def github_login(request):
    # Redirect users to the github login page
    code_verifier, code_hash = generate_pcke()
    print("Code verifier within login function")
    print(code_verifier)
    state = secrets.token_urlsafe(16)
    cache.set(f'pkce_{state}', code_verifier)
    client_ID = settings.GITHUB_CLIENT_ID
    callback_url='http://localhost:8000/auth/github/callback'
    url = f'https://github.com/login/oauth/authorize?client_id={client_ID}&redirect_uri={callback_url}&code_challenge={code_hash}&code_challenge_method=S256&state={state}'
    return 200, PassToClientSchema(authentication_url=url, state=state)

@api.get('/github/callback', response={ 200: dict, 400: dict, 500: dict })
def github_login_callback(request, code: str, state: str):
    try:
        # Handles the callback from github after user has authenticated
        code_verifier = cache.get(f'pkce_{state}')
        print("Code verifier outside login function")
        print(code_verifier)
        cache.delete(f'pkce_{state}')
        data = get_access_token(code, code_verifier)
        if data.get('error'):
            # cache.set(f'token_{state}', { 'error': data.get('error_description') })
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
            user.save()
        else:
            user= User.objects.create(github_id=github_id, email=email, username=username, avatar_url=avatar_url )
            user.set_unusable_password()
            user.save()

        token = create_user_access_token(user)
        print("Token within callback")
        print(token)
        cache.set(f'oauth_token_{state}', { 'access_token': token.access_token, 'refresh_token': token.refresh_token })
        print("Does cache have token?")
        print(cache.has_key(f'oauth_token_{state}'))
        return 200, { 'success': 'true', 'data': token }
    except Exception as e:
        print(e)
        cache.set(f'oauth_token_{state}', { 'error': 'An error occured.' })
        return 500, { 'success': False, 'message': 'An error occurred!!' }

@api.get('/github/poll')
def poll_github_for_token(request, state: str):
    print(state)
    result = cache.get(f'oauth_token_{state}')
    print("polling result")
    print(result)
    if not result:
        return 200, { "status": "pending" }
    if result.get('error'):
        return 200, { 'status': 'error', 'message': result.get('error') }
    return 200, { 'status': 'success', 'data': result}


@api.post('/refresh', response={
    200: TokenPairOutputResponseSchema, 401: ErrorResponse, 404: ErrorResponse, 500: ErrorResponse
})
def refresh_access_token(request, payload: TokenRefreshInputSchema):
    try:
        refresh = jwt.decode(payload.refresh_token, settings.JWT_SECRET, algorithms=[settings.JWT_SECRET_ALGORITHM])

        if refresh['type'] != 'refresh':
            return 400, errorHandler(400, "Please provide valid refresh token")
        user = User.objects.get(id=uuid.UUID(refresh['user_id']))
        token = create_user_access_token(user)
        return 200, TokenPairOutputResponseSchema(status='success', data=TokenPairOutputSchema(access_token=str(token.access_token), refresh_token=str(token.refresh_token)))
    except jwt.ExpiredSignatureError:
        return 401, errorHandler(401, 'Refresh token is expired')
    except User.DoesNotExist:
        return 401, errorHandler(401, "Invalid refresh token")
    except Exception as e:
        return 500, errorHandler(500, 'An error occured.')


def create_user_access_token(user) -> TokenPairOutputSchema:
    # Implementation for creating user access token
    access_payload = {
        'user_id': str(user.id),
        'type': 'access',
        'exp': datetime.utcnow() + settings.JWT_ACCESS_EXP_TIME
    }
    refresh_payload = {
        'user_id': str(user.id),
        'type': 'refresh',
        'exp': datetime.utcnow() + settings.JWT_REFRESH_EXP_TIME
    }
    access_token = jwt.encode(access_payload, settings.JWT_SECRET, algorithm=settings.JWT_SECRET_ALGORITHM)
    refresh_token = jwt.encode(refresh_payload, settings.JWT_SECRET, algorithm=settings.JWT_SECRET_ALGORITHM)
    return TokenPairOutputSchema(access_token=access_token, refresh_token=refresh_token)

def get_access_token(code, code_verifier):
    response = requests.post(
        f'https://github.com/login/oauth/access_token',
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
