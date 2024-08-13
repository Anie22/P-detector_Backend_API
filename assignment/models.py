from django.db import models
from accounts.models import User

# Create your models here.

STATUS_CHOICES = [
    ('pending', 'Pending'),
    ('plagarized', 'Plagarized'),
]

class Assignment(models.Model):
    project_name = models.CharField(verbose_name='Project Name', max_length=80, unique=False)
    project_description = models.CharField(verbose_name='Project Description', max_length=250, unique=False)
    submission_deadline = models.DateTimeField(verbose_name='Submission Month and Time', auto_created=False, auto_now=False)
    date_given = models.DateTimeField(verbose_name='Given On', auto_created=True, auto_now_add=True)
    lecturer = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.project_name

class SubmittedAssignment(models.Model):
    project_name = models.CharField(verbose_name='Project Name', max_length=80)
    project_solution = models.FileField(verbose_name='Project Solution', upload_to='project_files')
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE)
    grade = models.CharField(verbose_name='Grade', max_length=15, blank=True)
    status = models.CharField(verbose_name='Satus of Assignment', max_length=15, choices=STATUS_CHOICES, default='pending')
    submitted_on = models.DateTimeField(verbose_name='Submitted On', auto_now_add=True)
    student = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.student.firstName

class PlagiarismCheck(models.Model):
    file1 = models.ForeignKey(SubmittedAssignment, on_delete=models.CASCADE, related_name='file1')
    file2 = models.ForeignKey(SubmittedAssignment, on_delete=models.CASCADE, related_name='file2')
    similarity_score = models.FloatField(verbose_name='Plagiarism Score', blank=True, null=True)
    checked_on = models.DateTimeField(verbose_name='Checked on', auto_created=True, auto_now_add=True)
    lecturer = models.ForeignKey(User, on_delete=models.CASCADE, default=True)

    def __str__(self):
        return f'Plagiarism check between {self.file1.project_solution} and {self.file2.project_solution}'