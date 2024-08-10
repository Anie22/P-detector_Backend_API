from django.urls import path
from assignment.views import *

urlpatterns = [
    path('upload-assignment', AssignmentView.as_view()),
    path('assignment-list', StudentAssignmentListView.as_view()),
    path('lecturers_assignment-list', LecturerAssignmentListView.as_view()),
    path('update-assignment/<int:pk>/', UpdateAssignment.as_view()),
    path('submit', SubmitAssignmentView.as_view()),
    path('student-submission', StudentSubmittedView.as_view()),
    path('lecturer-student-submission-view', LecturerSubmittedView.as_view())
]