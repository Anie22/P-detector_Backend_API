from django.contrib import admin
from assignment.models import *
from django.utils.html import format_html

# Register your models here.

class AssignmentAdmin(admin.ModelAdmin):
    list_display = ['project_name', 'project_description', 'submission_deadline', 'date_given', 'lecturer']
    filter_horizontal = ()
    fieldsets = ()
    readonly_fields = ('date_given',)

    add_fieldsets=(
        (None, {
            'classes':('wide'),
            'fields':('project_name', 'project_description', 'submission_deadline', 'date_given', 'lecturer')
        }),
    )

    ordering=('lecturer',)

class SubmittedAdmin(admin.ModelAdmin):
    list_display = ['project_name', 'project_solution', 'assignment', 'grade', 'status', 'student']
    filter_horizontal = ()
    readonly_fields = ('submitted_on',)
    fieldsets = ()

    add_fieldsets=(
        (None, {
            'classes':('wide'),
            'fields':('project_name', 'project_solution', 'assignment', 'grade', 'status', 'submitted_on', 'student')
        }),
    )

    ordering=('student',)

    def Image(self, obj):
        return format_html('<img src="{}" style="max-width:90px; max-height:90px"/>'.format(obj.image.url))

class PlagiarismCheckAdmin(admin.ModelAdmin):
    list_display = ['file1', 'file2', 'similarity_score', 'checked_on', 'lecturer']
    filter_horizontal = ()
    fieldsets = ()
    readonly_fields = ('checked_on',)

    add_fieldset=(
        (None, {
            'classes':('wide'),
            'fields':('file1', 'file2', 'similarity_score', 'checked_on', 'lecturer')
        }),
    )

admin.site.register(Assignment, AssignmentAdmin)
admin.site.register(SubmittedAssignment, SubmittedAdmin)
admin.site.register(PlagiarismCheck, PlagiarismCheckAdmin)