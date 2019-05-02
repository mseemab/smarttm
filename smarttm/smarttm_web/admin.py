from django.contrib import admin

# Register your models here.
from smarttm_web.models import Participation_Type, Position, User, Club, Participation, Member, EC_Member, Meeting, Evaluation

class PositionAdmin(admin.ModelAdmin):
    list_display = ('name', 'seniority')

class UserAdmin(admin.ModelAdmin):
    list_display = ('email', 'full_name', 'is_staff', 'is_admin', 'last_login', 'get_groups')

class ParticipationTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'category')

admin.site.register(Participation_Type, ParticipationTypeAdmin)
admin.site.register(User, UserAdmin)
admin.site.register(Position, PositionAdmin)
admin.site.register(Club)
admin.site.register(Participation)
admin.site.register(Member)
admin.site.register(EC_Member)
admin.site.register(Meeting)
admin.site.register(Evaluation)
