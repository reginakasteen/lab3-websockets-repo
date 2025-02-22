from django.contrib import admin
from api.models import User, Profile, Task, Message

class UserAdmin(admin.ModelAdmin):
    list_display = ['username', 'email']


class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'name', 'gender', 'date_of_birth', 'is_online']
    list_editable = ['gender', 'date_of_birth', 'is_online']


class TaskAdmin(admin.ModelAdmin):    
    list_editable = [ 'completed',]

    list_display = ['title', 'user', 'completed', 'date']

class MessageAdmin(admin.ModelAdmin):    
    list_editable = [ 'is_read',]

    list_display = ['sender', 'receiver', 'is_read', 'message', 'date',]

admin.site.register(User, UserAdmin)
admin.site.register(Profile, ProfileAdmin)
admin.site.register(Task, TaskAdmin)
admin.site.register(Message, MessageAdmin)