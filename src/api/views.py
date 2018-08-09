from django.http import JsonResponse
from .decorators import api_decorator, required_fields
from accounts.models import User
from django.core.exceptions import ObjectDoesNotExist


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

    return JsonResponse({"success": True})
