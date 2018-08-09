from django.http import JsonResponse
from .decorators import api_decorator, required_fields
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
    try:
        user = User.objects.get(email=request.json_body['email'])
    except ObjectDoesNotExist:
        user = None
    if user and user.sign_up_finished:
        return JsonResponse({"error": "User with that email address already exists"}, status=400)
    else:
        user = User.objects.create(email=request.json_body['email'],
                                   first_name=request.json_body['firstName'],
                                   last_name=request.json_body['lastName'])
        user.set_password(request.json_body['password'])
        user.save()
    return JsonResponse({"data": {
        "token": _generate_token_for_user(user),
    }})
