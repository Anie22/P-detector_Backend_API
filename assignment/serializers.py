from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from accounts.models import User
from assignment.models import *
from assignment.utils import send_assignment_notification
from django.utils import timezone

class StudentAssignmentListSerializer(serializers.ModelSerializer):
    project_name = serializers.CharField(max_length=30, min_length=5, read_only=True)
    project_description = serializers.CharField(max_length=30, min_length=5, read_only=True)
    submission_deadline = serializers.DateTimeField(read_only=True)
    date_given = serializers.DateTimeField(read_only=True)
    lecturer = serializers.CharField(max_length=10, read_only=True)

    class Meta:
        model = Assignment
        fields = '__all__'



class LecturerAssignmentListSerializer(serializers.ModelSerializer):
    project_name = serializers.CharField(max_length=30, min_length=5, read_only=True)
    project_description = serializers.CharField(max_length=30, min_length=5, read_only=True)
    submission_deadline = serializers.DateTimeField(read_only=True)
    date_given = serializers.DateTimeField(read_only=True)
    lecturer = serializers.CharField(max_length=10, read_only=True)

    class Meta:
        model = Assignment
        fields = '__all__'

class AssignmentSerializer(serializers.ModelSerializer):
    project_name = serializers.CharField(max_length=30, min_length=5)
    project_description = serializers.CharField(max_length=30, min_length=5)
    submission_deadline = serializers.DateTimeField()
    date_given = serializers.DateTimeField(read_only=True)
    lecturer = serializers.CharField(max_length=10, read_only=True)

    class Meta:
        model = Assignment
        fields = ['project_name', 'project_description', 'submission_deadline', 'date_given', 'lecturer']

    def validate_submission_deadline(self, value):
        if value <= timezone.now():
            raise serializers.ValidationError('Submission date must be a future date')
        return value

    def create(self, validated_data):
        request = self.context.get('request')
        lecturer = request.user if request else None

        if not lecturer:
            raise serializers.ValidationError('Lecturer not found')

        assignment = Assignment.objects.create(
            project_name = validated_data.get('project_name'),
            project_description = validated_data.get('project_description'),
            submission_deadline = validated_data.get('submission_deadline'),
            date_given = validated_data.get('date_given'),
            lecturer = lecturer
        )

        students = User.objects.filter(account_type='Student')
        student_email = [student.email for student in students if student]

        if not student_email:
            raise serializers.ValidationError('Students not found in database')

        assignment_notification = {
            'email_subject': 'Assignment',
            'email_body': f'Good day {students}, Professor {assignment.lecturer} hav given a new assignment title {assignment.project_name}. Description: {assignment.project_description}. Note this assignment is to be submited on {assignment.submission_deadline}',
            'to_email': student_email
        }
        send_assignment_notification(assignment_notification)
        return assignment

    def update(self, instance, validated_data):
        request = self.context.get('request')
        lecturer = request.user if request else None

        if not lecturer:
            raise serializers.ValidationError('Lecturer not found')

        instance.project_name = validated_data.get('project_name', instance.project_name),
        instance.project_description = validated_data.get('project_description', instance.project_description),
        instance.submission_deadline = validated_data.get('submission_deadline', instance.submission_deadline),
        instance.lecturer = lecturer

        instance.save()