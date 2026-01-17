from rest_framework import generics, status
from rest_framework.response import Response
from django.db.models import Count, Q
from .models import Employee, Attendance
from .serializers import EmployeeSerializer, AttendanceSerializer
from rest_framework.views import APIView
import calendar
from datetime import datetime
from django.utils.dateparse import parse_date

class EmployeeListCreateView(generics.ListCreateAPIView):
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer

class EmployeeDeleteView(generics.DestroyAPIView):
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer
    lookup_field = 'id'

class AttendanceCreateView(generics.CreateAPIView):
    queryset = Attendance.objects.all()
    serializer_class = AttendanceSerializer

class AttendanceListByEmployeeView(generics.ListAPIView):
    serializer_class = AttendanceSerializer

    def get_queryset(self):
        employee_id = self.kwargs['employee_id']
        queryset = Attendance.objects.filter(employee_id=employee_id)

        date = self.request.query_params.get('date')
        if date:
            queryset = queryset.filter(date=date)

        return queryset

class DashboardSummaryView(APIView):
    def get(self, request):
        total_employees = Employee.objects.count()
        total_attendance = Attendance.objects.count()
        total_present = Attendance.objects.filter(status='PRESENT').count()
        total_absent = Attendance.objects.filter(status='ABSENT').count()
        

        current_month = datetime.now().month
        current_year = datetime.now().year
        
        current_month_present = Attendance.objects.filter(
            status='PRESENT',
            date__month=current_month,
            date__year=current_year
        ).count()
        
        current_month_absent = Attendance.objects.filter(
            status='ABSENT',
            date__month=current_month,
            date__year=current_year
        ).count()

        return Response({
            "total_employees": total_employees,
            "total_attendance_records": total_attendance,
            "total_present_days": total_present,
            "total_absent_days": total_absent,
            "current_month_present": current_month_present,
            "current_month_absent": current_month_absent,
            "attendance_rate_percentage": round((total_present / total_attendance * 100) if total_attendance > 0 else 0, 2)
        })


class EmployeePresentDaysView(APIView):
    def get(self, request):
        employees = Employee.objects.annotate(
            total_present_days=Count(
                'attendances',
                filter=Q(attendances__status='PRESENT')
            ),
            total_absent_days=Count(
                'attendances',
                filter=Q(attendances__status='ABSENT')
            )
        )

        serializer = EmployeeSerializer(employees, many=True)
        return Response(serializer.data)


class HRAttendanceFilterView(APIView):
    def get(self, request):

        employee_name = request.query_params.get('employee_name', '').strip()
        month = request.query_params.get('month')
        year = request.query_params.get('year')

        if not year:
            year = datetime.now().year
        

        attendance_queryset = Attendance.objects.all().select_related('employee')

        if employee_name:
            attendance_queryset = attendance_queryset.filter(
                Q(employee__full_name__icontains=employee_name) |
                Q(employee__employee_id__icontains=employee_name)
            )
        

        if month:
            try:
                month_int = int(month)
                if 1 <= month_int <= 12:
                    attendance_queryset = attendance_queryset.filter(
                        date__month=month_int,
                        date__year=int(year)
                    )
                    

                    _, total_days_in_month = calendar.monthrange(int(year), month_int)
                else:
                    return Response(
                        {"error": "Month must be between 1 and 12"},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            except ValueError:
                return Response(
                    {"error": "Invalid month format"},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
  
        employee_summary = {}
        attendance_data = []
        
        for attendance in attendance_queryset:
            employee_id = attendance.employee.id
            
            if employee_id not in employee_summary:
                employee_summary[employee_id] = {
                    'employee': {
                        'id': attendance.employee.id,
                        'employee_id': attendance.employee.employee_id,
                        'full_name': attendance.employee.full_name,
                        'email': attendance.employee.email,
                        'department': attendance.employee.department
                    },
                    'total_present': 0,
                    'total_absent': 0,
                    'attendance_records': []
                }
            
            if attendance.status == 'PRESENT':
                employee_summary[employee_id]['total_present'] += 1
            elif attendance.status == 'ABSENT':
                employee_summary[employee_id]['total_absent'] += 1
            

            employee_summary[employee_id]['attendance_records'].append({
                'date': attendance.date,
                'status': attendance.status
            })
            
      
            attendance_data.append({
                'id': attendance.id,
                'employee_id': attendance.employee.id,
                'employee_name': attendance.employee.full_name,
                'employee_code': attendance.employee.employee_id,
                'date': attendance.date,
                'status': attendance.status
            })
        
      
        summary_list = []
        for emp_id, summary in employee_summary.items():
            summary_list.append({
                'employee_info': summary['employee'],
                'total_present': summary['total_present'],
                'total_absent': summary['total_absent'],
                'attendance_rate': round(
                    (summary['total_present'] / (summary['total_present'] + summary['total_absent']) * 100)
                    if (summary['total_present'] + summary['total_absent']) > 0 else 0,
                    2
                ),
                'attendance_records': summary['attendance_records']
            })
        

        total_employees_in_report = len(employee_summary)
        total_records = len(attendance_data)
        overall_present = sum(s['total_present'] for s in summary_list)
        overall_absent = sum(s['total_absent'] for s in summary_list)
        
        response_data = {
            'filters_applied': {
                'employee_name': employee_name if employee_name else 'All',
                'month': month if month else 'All',
                'year': year
            },
            'summary': {
                'total_employees_in_report': total_employees_in_report,
                'total_attendance_records': total_records,
                'overall_present': overall_present,
                'overall_absent': overall_absent,
                'overall_attendance_rate': round(
                    (overall_present / total_records * 100) if total_records > 0 else 0,
                    2
                )
            },
            'employee_summary': summary_list,
            'detailed_attendance': attendance_data
        }
        
 
        if month:
            response_data['filters_applied']['total_working_days_in_month'] = total_days_in_month
        
        return Response(response_data)