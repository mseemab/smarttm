from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
# Create your models here.
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token
from django.utils import timezone
from smarttm_web.middleware import get_username

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

    def save(self, *args, **kwargs):

        self.created_by = get_username() if self.created_by is None else self.created_by
        self.updated_by = get_username()
        self.created_date = timezone.now() if self.created_date is None else self.created_date
        self.updated_date = timezone.now()

        super(UserManager, self).save(*args, **kwargs)

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
    country = models.CharField(max_length=20, null = True, blank = True)
    paid_until = models.DateTimeField('Expiry Date', null = True, blank = True)
    created_date = models.DateTimeField('Date Created', default= timezone.now, blank = True)
    updated_date = models.DateTimeField('Date Updated', default= timezone.now, blank = True)
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

    def save(self, *args, **kwargs):
        req_user = get_username()
        if not req_user.is_anonymous:
            self.created_by = req_user if self.created_by is None else self.created_by
            self.updated_by = req_user
        self.created_date = timezone.now() if self.created_date is None else self.created_date
        self.updated_date = timezone.now()

        super(User, self).save(*args, **kwargs)
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
    
    def save(self, *args, **kwargs):

        self.created_by = get_username() if self.created_by is None else self.created_by
        self.updated_by = get_username()
        self.created_date = timezone.now() if self.created_date is None else self.created_date
        self.updated_date = timezone.now()

        super(Club, self).save(*args, **kwargs)

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

    def save(self, *args, **kwargs):

        self.created_by = get_username() if self.created_by is None else self.created_by
        self.updated_by = get_username()
        self.created_date = timezone.now() if self.created_date is None else self.created_date
        self.updated_date = timezone.now()

        super(Position, self).save(*args, **kwargs)

    def __str__(self):
        return self.name    

class Member(models.Model):
    user = models.ForeignKey(User, related_name='member_user', on_delete=models.CASCADE)
    active = models.BooleanField(default = True)
    status = models.BooleanField(default = True)
    club = models.ForeignKey(Club, on_delete=models.CASCADE)
    club_membership_date = models.DateField('Date Joined', null = True, blank = True)
    created_date = models.DateTimeField('Date Created', null = True, blank = True)
    updated_date = models.DateTimeField('Date Updated', null = True, blank = True)
    created_by = models.ForeignKey(User, related_name='member_created_by',on_delete=models.CASCADE, null = True, blank = True)
    updated_by = models.ForeignKey(User, related_name='member_updated_by',on_delete=models.CASCADE, null = True, blank = True)
    position = models.ForeignKey(Position, on_delete=models.CASCADE, null=True, blank=True)
    is_EC = models.BooleanField(default = False)

    def save(self, *args, **kwargs):

        self.created_by = get_username() if self.created_by is None else self.created_by
        self.updated_by = get_username()
        self.created_date = timezone.now() if self.created_date is None else self.created_date
        self.updated_date = timezone.now()

        super(Member, self).save(*args, **kwargs)

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

    def save(self, *args, **kwargs):

        self.created_by = get_username() if self.created_by is None else self.created_by
        self.updated_by = get_username()
        self.created_date = timezone.now() if self.created_date is None else self.created_date
        self.updated_date = timezone.now()

        super(EC_Member, self).save(*args, **kwargs)

    def __str__(self):
        return self.position.name + '__' + self.club.name +'__' + self.user.full_name

class Meeting(models.Model):
    club = models.ForeignKey(Club, on_delete=models.CASCADE)
    meeting_date = models.DateField('Meeting Date')
    created_date = models.DateTimeField('Date Created', null = True, blank = True)
    updated_date = models.DateTimeField('Date Updated', null = True, blank = True)
    created_by = models.ForeignKey(User, related_name='meeting_created_by',on_delete=models.CASCADE, null = True, blank = True)
    updated_by = models.ForeignKey(User, related_name='meeting_updated_by',on_delete=models.CASCADE, null = True, blank = True)

    def save(self, *args, **kwargs):

        self.created_by = get_username() if self.created_by is None else self.created_by
        self.updated_by = get_username()
        self.created_date = timezone.now() if self.created_date is None else self.created_date
        self.updated_date = timezone.now()

        super(Meeting, self).save(*args, **kwargs)

    def __str__(self):
        return str(self.meeting_date)+'__'+self.club.name

class Participation_Type(models.Model):
    name = models.CharField(max_length = 200)
    category = models.CharField(max_length = 20)
    created_date = models.DateTimeField('Date Created', null = True, blank = True)
    updated_date = models.DateTimeField('Date Updated', null = True, blank = True)
    created_by = models.ForeignKey(User, related_name='participationtype_created_by',on_delete=models.CASCADE, null = True, blank = True)
    updated_by = models.ForeignKey(User, related_name='participationtype_updated_by',on_delete=models.CASCADE, null = True, blank = True)

    def save(self, *args, **kwargs):

        self.created_by = get_username() if self.created_by is None else self.created_by
        self.updated_by = get_username()
        self.created_date = timezone.now() if self.created_date is None else self.created_date
        self.updated_date = timezone.now()

        super(Participation_Type, self).save(*args, **kwargs)

    def __str__(self):
        return self.name

class Participation(models.Model):
    club = models.ForeignKey(Club, on_delete=models.CASCADE, null = True, blank = True)
    meeting = models.ForeignKey(Meeting, on_delete=models.CASCADE)
    participation_type = models.ForeignKey(Participation_Type, on_delete=models.CASCADE)
    evaluation = models.ForeignKey('Evaluation', related_name='related_evaluation',on_delete= models.CASCADE, null = True, blank = True)
    time_seconds = models.IntegerField(default = 0)
    ah_count = models.IntegerField(default = 0)
    vote_count = models.IntegerField(default = 0)
    grammar_good = models.CharField(max_length = 200, null = True, blank = True)
    grammar_bad = models.CharField(max_length = 200, null = True, blank = True)
    grammar_remarks = models.CharField(max_length = 200, null = True, blank = True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null = True, blank = True)
    member = models.ForeignKey(Member, on_delete=models.CASCADE, null = True, blank = True)
    created_date = models.DateTimeField('Date Created', null = True, blank = True)
    updated_date = models.DateTimeField('Date Updated', null = True, blank = True)
    created_by = models.ForeignKey(User, related_name='participation_created_by',on_delete=models.CASCADE, null = True, blank = True)
    updated_by = models.ForeignKey(User, related_name='participation_updated_by',on_delete=models.CASCADE, null = True, blank = True)

    def save(self, *args, **kwargs):

        self.created_by = get_username() if self.created_by is None else self.created_by
        self.updated_by = get_username()
        self.created_date = timezone.now() if self.created_date is None else self.created_date
        self.updated_date = timezone.now()

        super(Participation, self).save(*args, **kwargs)

    def __str__(self):
        return str(self.meeting.meeting_date)+str(self.meeting.club.name) + '__' + str(self.participation_type.name)


class Evaluation(models.Model):
    participation = models.ForeignKey(Participation, related_name='related_participation', on_delete=models.CASCADE)
    remarks = models.CharField(max_length = 1000, null = True, blank = True)
    created_date = models.DateTimeField('Date Created', null = True, blank = True)
    updated_date = models.DateTimeField('Date Updated', null = True, blank = True)
    created_by = models.ForeignKey(User, related_name='evaluation_created_by',on_delete=models.CASCADE, null = True, blank = True)
    updated_by = models.ForeignKey(User, related_name='evaluation_updated_by',on_delete=models.CASCADE, null = True, blank = True)

    def save(self, *args, **kwargs):

        self.created_by = get_username() if self.created_by is None else self.created_by
        self.updated_by = get_username()
        self.created_date = timezone.now() if self.created_date is None else self.created_date
        self.updated_date = timezone.now()

        super(Evaluation, self).save(*args, **kwargs)

class Summary(models.Model):
    member = models.ForeignKey(Member, on_delete=models.CASCADE, null = True, blank = True)
    tt_count = models.IntegerField(default = 0)
    speeches_count = models.IntegerField(default = 0)
    basic_role_count = models.IntegerField(default = 0)
    adv_role_count = models.IntegerField(default = 0)
    evaluation_count = models.IntegerField(default = 0)

    def save(self, *args, **kwargs):

        self.created_by = get_username() if self.created_by is None else self.created_by
        self.updated_by = get_username()
        self.created_date = timezone.now() if self.created_date is None else self.created_date
        self.updated_date = timezone.now()

        super(Summary, self).save(*args, **kwargs)

    def __str__(self):
        return str(Participation)

class Meeting_Summary(models.Model):
    meeting = models.ForeignKey(Meeting, on_delete=models.CASCADE)
    speech_count = models.IntegerField(default=0)
    tt_count = models.IntegerField(default=0)
    prep_speech_count = models.IntegerField(default=0)