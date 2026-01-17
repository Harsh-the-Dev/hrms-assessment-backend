from rest_framework import serializers
from .models import Employee, Attendance

class EmployeeSerializer(serializers.ModelSerializer):
    total_present_days = serializers.IntegerField(read_only=True)

    class Meta:
        model = Employee
        fields = '__all__'

class AttendanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attendance
        fields = ['id', 'employee', 'date', 'status']

    def validate(self, data):
        if Attendance.objects.filter(employee=data['employee'], date=data['date']).exists():
            raise serializers.ValidationError("Attendance for this employee on this date already exists.")
        return data