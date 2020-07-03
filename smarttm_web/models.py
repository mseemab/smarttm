from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
# Create your models here.
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token
from django.utils import timezone
from smarttm_web.middleware import get_username
import pandas as pd

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

    def is_member(self, club_id):
        try:
            Member.objects.get(user=self, club_id=club_id, active=True, paid_status=True)
            return True
        except:
            return False

    def is_ec(self, club_id):
        try:
            Member.objects.get(user=self, club_id=club_id, active=True, paid_status=True, is_EC=True)
            return True
        except:
            return False

    def save(self, *args, **kwargs):
        req_user = get_username()
        if not req_user is None:
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

    def import_members(self, file):
        
        df = pd.read_csv(file)
        df = df.fillna(0)
        
        temp_columns = ["Customer ID", "Name", "Company / In Care Of", "Addr L1", "Addr L2", "Addr L3", "Addr L4", "Addr L5", "Country", "Member has opted-out of Toastmasters WHQ marketing mail", "Email", "Secondary Email", "Member has opted-out of Toastmasters WHQ marketing emails", "Home Phone", "Mobile Phone", "Additional Phone", "Member has opted-out of Toastmasters WHQ marketing phone calls", "Paid Until", "Member of Club Since", "Original Join Date", "status (*)", "Current Position", "Future Position", "Pathways Enrolled"]
        req_cols = {"Customer ID":True, "Name":True, "Company / In Care Of":False, "Addr L1":True, "Addr L2":False, "Addr L3":False, "Addr L4":False, "Addr L5":False, "Country":True, "Member has opted-out of Toastmasters WHQ marketing mail":False, "Email":True, "Secondary Email":False, "Member has opted-out of Toastmasters WHQ marketing emails":False, "Home Phone":False, "Mobile Phone":False, "Additional Phone":False, "Member has opted-out of Toastmasters WHQ marketing phone calls":False, "Paid Until":True, "Member of Club Since":False, "Original Join Date":False, "status (*)":True, "Current Position":False, "Future Position":False, "Pathways Enrolled":False}
        
        header = df.columns.tolist()
        if header == temp_columns:
            for key, value in req_cols.items():
                if value:
                    if df[key].isnull().values.any():
                        raise ValueError("values contain empty cell(s)!")
            # Data is valid. 
            user_list = []
            member_list = []


            for index, row in df.iterrows():

                #check if user exists already
                user_obj, created = User.objects.update_or_create(
                    email = row['Email'],
                    defaults = {'full_name':row['Name'],
                                "address" : row['Addr L1'],
                                "country" : row['Country'],
                                "home_phone" : row['Home Phone'],
                                "mobile_phone" : row['Mobile Phone'],
                                "address" : row['Addr L1'] + ' ' + row['Addr L1'] + ' ' + row['Addr L5'],
                                #"paid_until" : row['Paid Until'],
                                "toastmaster_id" : row['Customer ID']
                            }

                )

                paid_status = True if row['status (*)'] == 'paid' else False
                active = True
                is_ec = False if row['Current Position'] is None or row['Current Position'] == 0 else True

                user_list.append(user_obj)
                member_obj, created = Member.objects.update_or_create(
                    club = self, user = user_obj,
                    defaults={'paid_status' : paid_status,
                              'is_EC': is_ec,
                              'active': active}
                )

                member_list.append(member_obj)

            club_member_ids = list(self.members.filter(active = True).values_list('pk', flat = True))
            new_member_ids = [member.pk for member in member_list]
            inactive_member_ids = tuple(set(club_member_ids) - set(new_member_ids))
            Member.objects.filter(id__in = inactive_member_ids).update(paid_status = False, is_EC = False, active = False)
        else:
            raise ValueError("Template is not correct. Please check again!")

    def is_member(self, user):
        try:
            Member.objects.get(user=user, club=self, paid_status=True, active=True)
            return True
        except:
            return False

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
    paid_status = models.BooleanField(default = True)
    club = models.ForeignKey(Club, on_delete=models.CASCADE, related_name='members')
    club_membership_date = models.DateField('Date Joined', null = True, blank = True)
    created_date = models.DateTimeField('Date Created', null = True, blank = True)
    updated_date = models.DateTimeField('Date Updated', null = True, blank = True)
    created_by = models.ForeignKey(User, related_name='member_created_by',on_delete=models.CASCADE, null = True, blank = True)
    updated_by = models.ForeignKey(User, related_name='member_updated_by',on_delete=models.CASCADE, null = True, blank = True)
    position = models.ForeignKey(Position, on_delete=models.CASCADE, null=True, blank=True)
    is_EC = models.BooleanField(default = False)
    summary_sent_date = models.DateTimeField('Summary Sent Date', null = True, blank = True)

    def save(self, *args, **kwargs):

        self.created_by = get_username() if self.created_by is None else self.created_by
        self.updated_by = get_username()
        self.created_date = timezone.now() if self.created_date is None else self.created_date
        self.updated_date = timezone.now()

        super(Member, self).save(*args, **kwargs)

    def get_part_summary(self):
        member_summary = Member_Summary()
        part_types = Participation_Type.objects.all()
        cat_adv = part_types.filter(category='Role-Advanced')
        cat_adv_ids = [cat.id for cat in cat_adv]
        tt = part_types.get(name="Table Topic")
        eval = part_types.get(name="Evaluation")
        prep_speech = part_types.get(name="Prepared Speech")
        member_summary.prep_speech_count = Participation.objects.filter(member=self, participation_type_id=prep_speech.id).count()
        member_summary.tt_speech_count = Participation.objects.filter(member=self, participation_type_id=tt.id).count()
        member_summary.eval_speech_count = Participation.objects.filter(member=self, participation_type_id=eval.id).count()
        member_summary.adv_roles_count = Participation.objects.filter(member=self, participation_type_id__in=cat_adv_ids).count()
        member_summary.present_count = Attendance.objects.filter(member=self, present=True).count()
        member_summary.parts_count = Participation.objects.filter(member=self).count()
        member_summary.meeting_part_count = Participation.objects.filter(member=self).values('meeting_id').distinct().count()
        member_summary.member_name = self.user.full_name
        return member_summary

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
    meeting_no = models.CharField(max_length=20)
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

class Attendance(models.Model):
    member = models.ForeignKey(Member, on_delete=models.CASCADE)
    meeting = models.ForeignKey(Meeting, on_delete=models.CASCADE)
    present = models.BooleanField(default=False)
    created_date = models.DateTimeField('Date Created', null=True, blank=True)
    updated_date = models.DateTimeField('Date Updated', null=True, blank=True)
    created_by = models.ForeignKey(User, related_name='attendance_created_by', on_delete=models.CASCADE, null=True,
                                   blank=True)
    updated_by = models.ForeignKey(User, related_name='attendance_updated_by', on_delete=models.CASCADE, null=True,
                                   blank=True)

    def save(self, *args, **kwargs):

        self.created_by = get_username() if self.created_by is None else self.created_by
        self.updated_by = get_username()
        self.created_date = timezone.now() if self.created_date is None else self.created_date
        self.updated_date = timezone.now()

        super(Attendance, self).save(*args, **kwargs)

    @staticmethod
    def get_latest_absents(members_list):
        mems = [str(mem) for mem in members_list]

        data = Attendance.objects.raw('SELECT att.id, att.member_id, (SELECT ifnull(count(*), 0) \
FROM smarttm_web_attendance as abc \
WHERE abc.member_id = att.member_id and abc.present = 0 and abc.id > ifnull((SELECT mini_attendance.id FROM smarttm_web_attendance as mini_attendance WHERE mini_attendance.member_id = att.member_id and mini_attendance.present = 1 order by mini_attendance.id desc LIMIT 1),0) ) as count_absents \
FROM smarttm_web_attendance as att \
WHERE att.member_id in (%s)\
 group by att.member_id \
order by att.id DESC ' % ','.join(mems))

        return data
    def __str__(self):
        return self.meeting.club.name + '__' +str(self.meeting.meeting_date) + '__' + self.member.user.full_name

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
        att, created = Attendance.objects.update_or_create(member_id=self.member_id, meeting_id=self.meeting_id,
                                                           defaults={
                                                               'present': True,
                                                           }
                                                           )

        super(Participation, self).save(*args, **kwargs)

    def get_participation_count(members_list):
        mems = [str(mem) for mem in members_list]
        data = Participation.objects.raw('SELECT member_main.id, (SELECT count(member.id)\
 FROM smarttm_web_member member LEFT JOIN smarttm_web_attendance attendance on member.id = attendance.member_id, smarttm_web_meeting meeting\
 WHERE meeting.id = attendance.meeting_id and attendance.present = 1 and member.id = member_main.id) as TotalAttendance, \
(SELECT COUNT(DISTINCT(CONCAT(part.member_id, "_", part.meeting_id)))\
 FROM smarttm_web_member member LEFT JOIN smarttm_web_participation part on member.id = part.member_id, smarttm_web_meeting meeting\
 WHERE meeting.id = part.meeting_id and member.id = member_main.id) as TotalParticipations\
 FROM `smarttm_web_member` member_main\
 WHERE member_main.id IN (%s)' % ','.join(mems))

        return data
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
    ttm_count = models.IntegerField(default = 0)
    ge_count = models.IntegerField(default=0)
    toe_count = models.IntegerField(default=0)
    evaluation_count = models.IntegerField(default = 0)
    attendance_percent = models.IntegerField(default = 0)
    last_absents = models.IntegerField(default = 0)
    tt_percent = models.IntegerField(default = 0)
    part_percent = models.IntegerField(default = 0)
    ranking = models.IntegerField(default=0)

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
    members_present_count = models.IntegerField(default=0)
    members_absent_count = models.IntegerField(default=0)

class Member_Summary(models.Model):
    member_name = models.CharField(max_length = 100)
    prep_speech_count = models.IntegerField(default=0)
    tt_speech_count = models.IntegerField(default=0)
    eval_speech_count = models.IntegerField(default=0)
    adv_roles_count = models.IntegerField(default=0)
    present_count = models.IntegerField(default=0)
    parts_count = models.IntegerField(default=0)
    meeting_part_count = models.IntegerField(default=0)
