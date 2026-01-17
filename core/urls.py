from django.urls import path
from . import views

urlpatterns = [
    path('employees/', views.EmployeeListCreateView.as_view(), name='employee-list-create'),
    path('employees/<int:id>/', views.EmployeeDeleteView.as_view(), name='employee-delete'),
    path('attendance/', views.AttendanceCreateView.as_view(), name='attendance-create'),
    path('attendance/employee/<int:employee_id>/', views.AttendanceListByEmployeeView.as_view(), name='attendance-by-employee'),
    path('dashboard/summary/', views.DashboardSummaryView.as_view(), name='dashboard-summary'),
    path('employees/present-days/', views.EmployeePresentDaysView.as_view(), name='employee-present-days'),
    # NEW URL for HR attendance filtering
    path('hr/attendance-report/', views.HRAttendanceFilterView.as_view(), name='hr-attendance-report'),
]