from django.db import models

class Employee(models.Model):
    employee_id = models.CharField(max_length=20, unique=True)
    full_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    department = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.full_name} ({self.employee_id})"


class Attendance(models.Model):
    STATUS_CHOICES = (
    ('Present', 'Present'),
    ('Absent', 'Absent'),
    )

    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name='attendances'
    )
    date = models.DateField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES)

     

    def __str__(self):
        return f"{self.employee.full_name} - {self.date} - {self.status}"
