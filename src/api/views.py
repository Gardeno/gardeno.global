from django.http import JsonResponse
from .decorators import api_decorator, required_fields, authentication_required
from accounts.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings
import jwt


def _generate_token_for_user(user):
    return jwt.encode({"email": user.email}, settings.JWT_SECRET, algorithm='HS256').decode('utf-8')


@api_decorator(allowed_methods=['POST'])
@required_fields(['email', 'password'])
def accounts_sign_in(request):
    try:
        user = User.objects.get(email=request.json_body['email'])
    except ObjectDoesNotExist:
        user = None
    if not user or not user.check_password(request.json_body['password']):
        return JsonResponse({"error": "Unable to login, check email/password"}, status=400)
    return JsonResponse({"data": {
        "token": _generate_token_for_user(user),
    }})


@api_decorator(allowed_methods=['POST'])
@required_fields(['email', 'firstName', 'lastName', 'password'])
def accounts_sign_up(request):
    error, user = User.objects.create_user_with_info(email=request.json_body['email'],
                                                     first_name=request.json_body['firstName'],
                                                     last_name=request.json_body['lastName'],
                                                     password=request.json_body['password'])
    if error:
        return JsonResponse({"error": error}, status=400)
    return JsonResponse({"data": {
        "token": _generate_token_for_user(user),
    }})


@api_decorator(allowed_methods=['GET'])
@authentication_required()
def accounts_me(request):
    return JsonResponse({"data": {
        "email": request.user.email,
        "invitations": [],
        "grows": [x.to_json() for x in request.user.grows()],
        "team_memberships": [x.to_json() for x in request.user.team_memberships()],
    }})


@api_decorator(allowed_methods=['GET'])
@authentication_required()
def accounts_my_grows(request):
    return JsonResponse({"data": [x.to_json() for x in request.user.grows()]})
