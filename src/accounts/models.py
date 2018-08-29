from django.db import models
from django.contrib.auth.models import (
    BaseUserManager, AbstractBaseUser
)
from django.core.exceptions import ObjectDoesNotExist
from django.utils.timezone import now


class UserManager(BaseUserManager):
    def create_user(self, email, password=None):
        """
        Creates and saves a User with the given email and password.
        """
        if not email:
            raise ValueError('Users must have an email address')
        user = self.model(
            email=self.normalize_email(email),
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password):
        """
        Creates and saves a superuser with the given email and password.
        """
        user = self.create_user(
            email,
            password=password,
        )
        user.is_admin = True
        user.save(using=self._db)
        return user

    def create_user_with_info(self, email=None, first_name=None, last_name=None, password=None):
        try:
            user = User.objects.get(email=email)
        except ObjectDoesNotExist:
            user = None
        if user and user.sign_up_finished:
            return "User with that email address already exists", None
        else:
            user = User.objects.create(email=email,
                                       first_name=first_name,
                                       last_name=last_name)
            user.set_password(password)
            user.save()
        user.create_default_team()
        return None, user


class User(AbstractBaseUser):
    email = models.EmailField(
        verbose_name='email address',
        max_length=255,
        unique=True,
    )
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)

    grow_limit = models.IntegerField(default=10, null=True,
                                     help_text='Maximum number of grows this user can create. Enter 0 for unlimited grows.')

    first_name = models.CharField(max_length=255, null=True, blank=True)
    last_name = models.CharField(max_length=255, null=True, blank=True)

    # Sometimes we'll want to create a user as a result of another action. For example,
    # inviting a new user to a team will create the user, add the user to the team, but we will
    # want to allow the user to "register" for the first time.
    sign_up_finished = models.BooleanField(default=True)
    email_verified = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'

    def __str__(self):
        if self.first_name and self.last_name:
            return '{} {}'.format(self.first_name, self.last_name)
        elif self.first_name:
            return '{}'.format(self.first_name)
        elif self.last_name:
            return '{}'.format(self.last_name)
        return '{}'.format(self.email)

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return True

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True

    @property
    def is_staff(self):
        "Is the user a member of staff?"
        # Simplest possible answer: All admins are staff
        return self.is_admin

    def create_default_team(self):
        team, created_team = Team.objects.get_or_create(created_by_user=self)
        if created_team:
            team.name = "{}'s Team".format(self)
            team.save()
        TeamMembership.objects.create(user=self, team=team, date_joined=now())

    def grows(self):
        return []

    def team_memberships(self):
        memberships = TeamMembership.objects.filter(user=self)
        if memberships.count() == 0:
            self.create_default_team()
        return memberships

    def to_json(self):
        return {
            "id": self.id,
            "name": "{}".format(self),
            "email": "{}".format(self.email)
        }


class LaunchSignup(models.Model):
    date_created = models.DateTimeField(auto_now_add=True)
    email = models.EmailField(null=True)


class Team(models.Model):
    name = models.CharField(max_length=255, null=True)
    users = models.ManyToManyField(User, through="TeamMembership")
    created_by_user = models.ForeignKey(User, related_name='created_teams', on_delete=models.SET_NULL, null=True,
                                        blank=True)

    def to_json(self, include_users=True):
        result = {"name": self.name}
        if include_users:
            result["created_by_user"] = self.created_by_user.to_json()
            result["users"] = [x.to_json() for x in self.users.all()]
        return result

    def __str__(self):
        return self.name


class TeamMembership(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    date_joined = models.DateTimeField()

    def to_json(self, include_user=False):
        result = {
            "team": self.team.to_json(),
            "date_joined": self.date_joined,
        }
        if include_user:
            result["user"] = self.user.to_json()
        return result
