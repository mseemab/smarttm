from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
# Create your models here.
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token

class UserManager(BaseUserManager):
    def create_user(self, email, password=None):
        if not email:
            raise ValueError('Email must be set!')
        user = self.model(email=email)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password):
        user = self.create_user(email, password)
        user.is_admin = True
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user

    def get_by_natural_key(self, email_):
        return self.get(email=email_)

class User(AbstractBaseUser, PermissionsMixin):
    is_staff = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    full_name = models.CharField(max_length = 200)
    address = models.CharField(max_length = 1000, null = True, blank = True)
    email = models.CharField(max_length = 200, unique= True)
    secondary_email = models.CharField(max_length = 200, null = True, blank = True)
    mobile_phone = models.CharField(max_length = 200, null = True, blank = True)
    home_phone = models.CharField(max_length = 200, null = True, blank = True)
    status = models.CharField(max_length = 10, null = True, blank = True)
    membership_date = models.DateTimeField('Date Joined', null = True, blank = True)
    toastmaster_id = models.IntegerField(default = 0, null = True, blank = True)
    paid_until = models.DateTimeField('Expiry Date', null = True, blank = True)
    created_date = models.DateTimeField('Date Created', null = True, blank = True)
    updated_date = models.DateTimeField('Date Updated', null = True, blank = True)
    created_by = models.ForeignKey('self', related_name='user_created_by',on_delete=models.CASCADE, null = True, blank = True)
    updated_by = models.ForeignKey('self', related_name='user_updated_by',on_delete=models.CASCADE, null = True, blank = True)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    objects = UserManager()

    def get_groups(self):
        user_groups = self.groups.all()
        groups_str = ""
        for user_group in user_groups:
            groups_str = groups_str + ' ' + user_group.name + ','
        return groups_str 

    def __str__(self):
        return self.full_name

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)

class Club(models.Model):
    club_number = models.CharField(max_length = 15, null = True, blank = True)
    name = models.CharField(max_length = 200)
    address = models.CharField(max_length = 1000, null = True, blank = True)
    meetings_schedule = models.CharField(max_length = 50, null = True, blank = True)
    meeting_day = models.CharField(max_length = 15, null = True, blank = True)
    created_date = models.DateTimeField('Date Created', null = True, blank = True)
    updated_date = models.DateTimeField('Date Updated', null = True, blank = True)
    created_by = models.ForeignKey(User, related_name='club_created_by',on_delete=models.CASCADE, null = True, blank = True)
    updated_by = models.ForeignKey(User, related_name='club_updated_by',on_delete=models.CASCADE, null = True, blank = True)

    def __str__(self):
        return self.name

class Position(models.Model):
    name = models.CharField(max_length = 50)
    seniority = models.IntegerField(default = 0)
    created_date = models.DateTimeField('Date Created', null = True, blank = True)
    updated_date = models.DateTimeField('Date Updated', null = True, blank = True)
    status = models.CharField(max_length = 10, null = True, blank = True)
    created_by = models.ForeignKey(User, related_name='position_created_by',on_delete=models.CASCADE, null = True, blank = True)
    updated_by = models.ForeignKey(User, related_name='position_updated_by',on_delete=models.CASCADE, null = True, blank = True)
    
    def __str__(self):
        return self.name    

class Member(models.Model):
    user = models.ForeignKey(User, related_name='member_user', on_delete=models.CASCADE)
    active = models.BooleanField(default = True)
    status = models.BooleanField(default = True)
    club = models.ForeignKey(Club, on_delete=models.CASCADE)
    club_membership_date = models.DateTimeField('Date Joined', null = True, blank = True)
    created_date = models.DateTimeField('Date Created', null = True, blank = True)
    updated_date = models.DateTimeField('Date Updated', null = True, blank = True)
    created_by = models.ForeignKey(User, related_name='member_created_by',on_delete=models.CASCADE, null = True, blank = True)
    updated_by = models.ForeignKey(User, related_name='member_updated_by',on_delete=models.CASCADE, null = True, blank = True)
    
    def __str__(self):
        return self.user.full_name+'__'+self.club.name

class EC_Member(models.Model):
    club = models.ForeignKey(Club, on_delete=models.CASCADE)
    position = models.ForeignKey(Position, on_delete=models.CASCADE)
    user = models.ForeignKey(User, related_name='role_responsible',on_delete=models.CASCADE)
    member = models.ForeignKey(Member, on_delete=models.CASCADE)
    created_date = models.DateTimeField('Date Created', null = True, blank = True)
    updated_date = models.DateTimeField('Date Updated', null = True, blank = True)
    created_by = models.ForeignKey(User, related_name='ecmember_created_by',on_delete=models.CASCADE, null = True, blank = True)
    updated_by = models.ForeignKey(User, related_name='ecmember_updated_by',on_delete=models.CASCADE, null = True, blank = True)

    def __str__(self):
        return self.position.name + '__' + self.club.name +'__' + self.user.full_name

class Meeting(models.Model):
    club = models.ForeignKey(Club, on_delete=models.CASCADE)
    meeting_date = models.DateField('Meeting Date')
    created_date = models.DateTimeField('Date Created', null = True, blank = True)
    updated_date = models.DateTimeField('Date Updated', null = True, blank = True)
    created_by = models.ForeignKey(User, related_name='meeting_created_by',on_delete=models.CASCADE, null = True, blank = True)
    updated_by = models.ForeignKey(User, related_name='meeting_updated_by',on_delete=models.CASCADE, null = True, blank = True)

    def __str__(self):
        return str(self.meeting_date)+'__'+self.club.name

class Participation_Type(models.Model):
    name = models.CharField(max_length = 200)
    category = models.CharField(max_length = 20)
    created_date = models.DateTimeField('Date Created', null = True, blank = True)
    updated_date = models.DateTimeField('Date Updated', null = True, blank = True)
    created_by = models.ForeignKey(User, related_name='participationtype_created_by',on_delete=models.CASCADE, null = True, blank = True)
    updated_by = models.ForeignKey(User, related_name='participationtype_updated_by',on_delete=models.CASCADE, null = True, blank = True)

    def __str__(self):
        return self.name

class Participation(models.Model):
    meeting = models.ForeignKey(Meeting, on_delete=models.CASCADE)
    participation_type = models.ForeignKey(Participation_Type, on_delete=models.CASCADE)
    evaluation = models.ForeignKey('Evaluation', related_name='related_evaluation',on_delete= models.CASCADE, null = True, blank = True)
    time_seconds = models.IntegerField(default = 0)
    ah_count = models.IntegerField(default = 0)
    vote_count = models.IntegerField(default = 0)
    grammar_good = models.CharField(max_length = 200, null = True, blank = True)
    grammar_bad = models.CharField(max_length = 200, null = True, blank = True)
    grammar_remarks = models.CharField(max_length = 200, null = True, blank = True)
    user = models.ForeignKey(User, related_name = 'participation_responsible', on_delete=models.CASCADE)
    member = models.ForeignKey(Member, on_delete=models.CASCADE, null = True, blank = True)
    created_date = models.DateTimeField('Date Created', null = True, blank = True)
    updated_date = models.DateTimeField('Date Updated', null = True, blank = True)
    created_by = models.ForeignKey(User, related_name='participation_created_by',on_delete=models.CASCADE, null = True, blank = True)
    updated_by = models.ForeignKey(User, related_name='participation_updated_by',on_delete=models.CASCADE, null = True, blank = True)
    
    def __str__(self):
        return str(self.meeting.meeting_date)+str(self.meeting.club.name) + '__' + self.user.full_name + '__' + str(self.participation_type.name)

class Evaluation(models.Model):
    participation = models.ForeignKey(Participation, related_name='related_participation', on_delete=models.CASCADE)
    remarks = models.CharField(max_length = 1000, null = True, blank = True)
    created_date = models.DateTimeField('Date Created', null = True, blank = True)
    updated_date = models.DateTimeField('Date Updated', null = True, blank = True)
    created_by = models.ForeignKey(User, related_name='evaluation_created_by',on_delete=models.CASCADE, null = True, blank = True)
    updated_by = models.ForeignKey(User, related_name='evaluation_updated_by',on_delete=models.CASCADE, null = True, blank = True)

    def __str__(self):
        return str(Participation)

