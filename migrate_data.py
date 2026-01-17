#!/usr/bin/env python
import os
import sys
import django
import json

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hrms.settings')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

django.setup()

def migrate_to_postgres():
    from django.core.management import execute_from_command_line
    
    print("Starting migration to PostgreSQL...")
    
    # Run migrations
    execute_from_command_line(['manage.py', 'migrate'])
    
    # Load backup data if exists
    backup_file = 'db_backup.json'
    if os.path.exists(backup_file):
        print("Loading backup data...")
        execute_from_command_line(['manage.py', 'loaddata', backup_file])
    
    print("Migration completed!")

if __name__ == '__main__':
    migrate_to_postgres()