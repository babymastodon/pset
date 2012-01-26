from django.contrib import admin
from main.models import *

#admin.site.register(modelname)


class ClassNumberInline(admin.StackedInline):
    model = ClassNumber
    extra = 12

class ClassAdmin(admin.ModelAdmin):
    inlines = [ClassNumberInline]


admin.site.register(UserInfo)
admin.site.register(PendingHash)
admin.site.register(Class, ClassAdmin)
admin.site.register(ClassNumber)
admin.site.register(Party)
admin.site.register(UserClassData)
admin.site.register(Course)
admin.site.register(Activity)
admin.site.register(Comment)

