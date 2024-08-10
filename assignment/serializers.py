from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from accounts.models import User
from assignment.models import *
from assignment.utils import send_assignment_notification
from django.utils import timezone

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
        if not isinstance(value, str):
            raise serializers.ValidationError('Submission deadline must be a string in ISO 8601 format')

        try:
            value = timezone.datetime.fromisoformat(value)
        except ValueError as e:
            raise serializers.ValidationError(f'Submission deadline must be in ISO 8601 format, {str(e)}')

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

        instance.project_name = validated_data.get('project_name', instance.project_name)
        instance.project_description = validated_data.get('project_description', instance.project_description)
        instance.submission_deadline = validated_data.get('submission_deadline', instance.submission_deadline)
        instance.date_given = validated_data.get('date_given', instance.date_given)
        instance.lecturer = lecturer

        instance.save()


class StudentAssignmentListSerializer(serializers.ModelSerializer):
    project_name = serializers.CharField(max_length=30, min_length=5, read_only=True)
    project_description = serializers.CharField(max_length=30, min_length=5, read_only=True)
    submission_deadline = serializers.DateTimeField(read_only=True)
    date_given = serializers.DateTimeField(read_only=True)
    lecturer = serializers.CharField(max_length=10, read_only=True)

    class Meta:
        model = Assignment
        fields = ['id', 'project_name', 'project_description', 'submission_deadline', 'date_given', 'lecturer']


class LecturerAssignmentListSerializer(serializers.ModelSerializer):
    project_name = serializers.CharField(max_length=30, min_length=5, read_only=True)
    project_description = serializers.CharField(max_length=30, min_length=5, read_only=True)
    submission_deadline = serializers.DateTimeField(read_only=True)
    date_given = serializers.DateTimeField(read_only=True)

    class Meta:
        model = Assignment
        fields = ['id', 'project_name', 'project_description', 'submission_deadline', 'date_given']


class SubmissionSerializer(serializers.ModelSerializer):
    project_name = serializers.CharField(max_length=80)
    project_solution = serializers.FileField()
    assignment = serializers.CharField(max_length=10)
    grade = serializers.CharField(max_length=15)
    status = serializers.CharField(max_length=10)
    submitted_on = serializers.DateTimeField(read_only=True)
    student = serializers.CharField(max_length=10, read_only=True)

    class Meta:
        model = SubmittedAssignment
        fields = ['project_name', 'project_solution', 'assignment', 'grade', 'status', 'submitted_on', 'student']

    def create(self, validated_data):
        request = self.context.get('request')
        student = request.user if request else None

        if student:
            assignment_no = validated_data.get('assignment')
            assignment = Assignment.objects.get(id=assignment_no)

            submissions = SubmittedAssignment.objects.create(
                project_name = validated_data.get('project_name'),
                project_solution = validated_data.get('project_solution'),
                assignment = assignment,
                grade = validated_data.get('grade'),
                status = validated_data.get('status'),
                submitted_on = validated_data.get('submitted_on'),
                student = student
            )
            return submissions
        else:
            raise serializers.ValidationError('Student not found')

class StudentSubmittedListSerializer(serializers.ModelSerializer):
    project_name = serializers.CharField(max_length=80, read_only=True)
    project_solution = serializers.FileField(read_only=True)
    assignment = serializers.CharField(max_length=10, read_only=True)
    grade = serializers.CharField(max_length=15, read_only=True)
    status = serializers.CharField(max_length=10, read_only=True)
    submitted_on = serializers.DateTimeField(read_only=True)

    class Meta:
        model = SubmittedAssignment
        fields = ['id', 'project_name', 'project_solution', 'assignment', 'grade', 'status', 'submitted_on']

class LecturerSubmittedListSerializer(serializers.ModelSerializer):
    project_name = serializers.CharField(max_length=80, read_only=True)
    project_solution = serializers.FileField(read_only=True)
    assignment = serializers.CharField(max_length=10, read_only=True)
    grade = serializers.CharField(max_length=15, read_only=True)
    status = serializers.CharField(max_length=10, read_only=True)
    submitted_on = serializers.DateTimeField(read_only=True)
    student = serializers.CharField(max_length=10, read_only=True)

    class Meta:
        model = SubmittedAssignment
        fields = ['id', 'project_name', 'project_solution', 'assignment', 'grade', 'status', 'submitted_on', 'student']