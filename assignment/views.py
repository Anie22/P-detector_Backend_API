from django.shortcuts import render
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.renderers import JSONRenderer
from rest_framework import status
from django.db import IntegrityError
from assignment.models import *
from assignment.serializers import *
from assignment.renders import AssignmentAPI

# Create your views here.

class AssignmentView(GenericAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    renderer_classes = [AssignmentAPI, JSONRenderer]
    serializer_class = AssignmentSerializer

    def get_queryset(self):
        return Assignment.objects.none()

    def post(self, request):
        assignment = request.data
        serializer = self.serializer_class(data=assignment, context={'request': request})

        try:
            if serializer.is_valid(raise_exception=True):
                serializer.save()
                return Response({
                    'message': 'Assignment have been uploaded successfully'
                }, status=status.HTTP_201_CREATED)
            return Response(serializer.error, status=status.HTTP_400_BAD_REQUEST)
        except IntegrityError as e:
            return Response({'message': f'A server error occurred {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class StudentAssignmentListView(GenericAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    renderer_classes = [AssignmentAPI, JSONRenderer]
    queryset = Assignment.objects.all()
    serializer_class = StudentAssignmentListSerializer

    def get(self, request):
        assignment = self.get_queryset()
        serializer = self.get_serializer(assignment, many=True)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class LecturerAssignmentListView(GenericAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    renderer_classes = [AssignmentAPI, JSONRenderer]
    serializer_class = LecturerAssignmentListSerializer

    queryset = Assignment.objects.all()

    def get(self, request):
        user = self.request.user
        assign = Assignment.objects.filter(lecturer=user)
        serializer = self.get_serializer(assign, many=True)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class UpdateAssignmentView(GenericAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    renderer_classes = [AssignmentAPI, JSONRenderer]
    serializer_class = AssignmentSerializer
    queryset = Assignment.objects.all()

    def put(self, request, pk, format=None):
        try:
            assign = Assignment.objects.get(pk=pk)
        except Assignment.DoesNotExist:
            return Response({'message': 'Assignment not found'}, status=status.HTTP_404_NOT_FOUND)

        serializer = self.serializer_class(assign, data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Assignment updated successfully'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class SubmitAssignmentView(GenericAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    renderer_classes = [AssignmentAPI, JSONRenderer]
    serializer_class = SubmissionSerializer

    def get_queryset(self):
        return SubmittedAssignment.objects.none()

    def post(self, request):
        submission = request.data
        serializer = self.serializer_class(data=submission, context={'request': request})

        try:
            if serializer.is_valid():
                serializer.save()
                return Response({
                    'message': 'Assignment Submitted Successfully'
                }, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except IntegrityError as e:
            return Response({'message': f'A server error occurred {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class StudentSubmissionView(GenericAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    renderer_classes = [AssignmentAPI, JSONRenderer]
    queryset = SubmittedAssignment.objects.all()
    serializer_class = StudentSubmissionListSerializer

    def get(self, request):
        user = self.request.user
        submitted = SubmittedAssignment.objects.filter(student=user)
        serializer = self.get_serializer(submitted, many=True)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class LecturerStudentSubmissionView(GenericAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    renderer_classes = [AssignmentAPI, JSONRenderer]
    queryset = SubmittedAssignment.objects.all()
    serializer_class = LecturerStudentSubmissionListSerializer

    def get(self, request):
        submission_data = self.get_queryset()
        serializer = self.get_serializer(submission_data, many=True)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class PlagiarismCheckerView(GenericAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    renderer_classes = [AssignmentAPI, JSONRenderer]
    queryset = PlagiarismCheck.objects.all()
    serializer_class = PlagiarismCheckSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data, context={'request':request})
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)