from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from accounts.models import User
from assignment.models import *
from assignment.utils import send_assignment_notification
from assignment.plagarism import check_plagiarism
from django.utils import timezone

class AssignmentSerializer(serializers.ModelSerializer):
    project_name = serializers.CharField(max_length=30, min_length=5)
    project_description = serializers.CharField(max_length=30, min_length=5)
    submission_deadline = serializers.DateTimeField(format='%Y-%M-%dT%H:%M:%S.%fZ')
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

        instance.project_name = validated_data.get('project_name', instance.project_name)
        instance.project_description = validated_data.get('project_description', instance.project_description)
        instance.submission_deadline = validated_data.get('submission_deadline', instance.submission_deadline)
        instance.date_given = validated_data.get('date_given', instance.date_given)
        instance.lecturer = lecturer

        instance.save()

        return instance


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

class StudentSubmissionListSerializer(serializers.ModelSerializer):
    project_name = serializers.CharField(max_length=80, read_only=True)
    project_solution = serializers.FileField(read_only=True)
    assignment = serializers.CharField(max_length=10, read_only=True)
    grade = serializers.CharField(max_length=15, read_only=True)
    status = serializers.CharField(max_length=10, read_only=True)
    submitted_on = serializers.DateTimeField(read_only=True)

    class Meta:
        model = SubmittedAssignment
        fields = ['id', 'project_name', 'project_solution', 'assignment', 'grade', 'status', 'submitted_on']

class LecturerStudentSubmissionListSerializer(serializers.ModelSerializer):
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

class PlagiarismCheckSerializer(serializers.ModelSerializer):
    file1 = serializers.CharField(write_only=True)
    file2 = serializers.CharField(write_only=True)
    similarity_score = serializers.FloatField(read_only=True)
    checked_on = serializers.DateTimeField(read_only=True)
    lecturer = serializers.CharField(read_only=True)

    class Meta:
        model = PlagiarismCheck
        fields = ['file1', 'file2', 'similarity_score', 'checked_on', 'lecturer']

    def validate(self, data):
        file1 = SubmittedAssignment.objects.get(id=data['file1'])
        file2 = SubmittedAssignment.objects.get(id=data['file2'])

        if file1.id == file2.id:
            raise serializers.ValidationError('Comparison of the same file is prihobited')

        file1_data = PlagiarismCheck.objects.filter(file1=file1).exists()
        file2_data = PlagiarismCheck.objects.filter(file2=file2).exists()

        if file1_data and file2_data:
            raise serializers.ValidationError('Files have already been compared and graded and cannot be use twise')

    def create(self, validated_data):
        file1 = SubmittedAssignment.objects.get(id=validated_data['file1'])
        file2 = SubmittedAssignment.objects.get(id=validated_data['file2'])
        request = self.context.get('request')
        lecturer = request.user if request else None

        similarity_score = check_plagiarism(file1.project_solution.path, file2.project_solution.path)

        file1.grade = self.calculate_grade(similarity_score)
        file2.grade = self.calculate_grade(similarity_score)

        file1.save()
        file2.save()

        plagiarism_check = PlagiarismCheck.objects.create(
            file1=file1,
            file2=file2,
            similarity_score=similarity_score,
            checked_on=validated_data.get('checked_on'),
            lecturer=lecturer
        )

        return plagiarism_check

    def calculate_grade(self, similarity_score):

        if similarity_score >= 0 and similarity_score <= 30:
            grade = 'A'
        elif similarity_score >= 30 and similarity_score <= 50:
            grade = 'B'
        elif similarity_score >= 50 and similarity_score <= 59:
            grade = 'C'
        elif similarity_score >= 59 and similarity_score <= 75:
            grade = 'D'
        elif similarity_score >= 75 and similarity_score <= 85:
            grade = 'E'
        elif similarity_score >= 85 and similarity_score == 100:
            grade = 'F'

        return grade