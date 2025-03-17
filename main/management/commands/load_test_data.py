from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from main.models import Department, Student, Staff

User = get_user_model()

class Command(BaseCommand):
    help = 'Загружает тестовые данные в базу данных'

    def handle(self, *args, **kwargs):
        # Создаем отделы
        departments = [
            {
                'name': 'Информационные технологии',
                'description': 'Отдел, отвечающий за IT-направления и компьютерные науки'
            },
            {
                'name': 'Бизнес и экономика',
                'description': 'Отдел, отвечающий за экономические специальности'
            },
            {
                'name': 'Иностранные языки',
                'description': 'Отдел, отвечающий за языковые специальности'
            },
            {
                'name': 'Технические специальности',
                'description': 'Отдел, отвечающий за технические направления'
            }
        ]

        created_departments = []
        for dept_data in departments:
            department, created = Department.objects.get_or_create(
                name=dept_data['name'],
                defaults={'data': {'description': dept_data['description']}}
            )
            created_departments.append(department)
            self.stdout.write(f'Создан отдел: {department.name}')

        # Создаем персонал
        staff_data = [
            {
                'username': 'ivanov_teacher',
                'password': 'testpass123',
                'first_name': 'Иван',
                'last_name': 'Иванов',
                'email': 'ivanov@example.com',
                'role': 'staff',
                'department': created_departments[0],
                'position': 'Преподаватель',
                'experience_years': 5,
                'student_count': 30
            },
            {
                'username': 'petrov_teacher',
                'password': 'testpass123',
                'first_name': 'Петр',
                'last_name': 'Петров',
                'email': 'petrov@example.com',
                'role': 'staff',
                'department': created_departments[1],
                'position': 'Старший преподаватель',
                'experience_years': 8,
                'student_count': 45
            },
            {
                'username': 'sidorov_teacher',
                'password': 'testpass123',
                'first_name': 'Сергей',
                'last_name': 'Сидоров',
                'email': 'sidorov@example.com',
                'role': 'staff',
                'department': created_departments[2],
                'position': 'Преподаватель',
                'experience_years': 3,
                'student_count': 25
            }
        ]

        for staff_info in staff_data:
            user, created = User.objects.get_or_create(
                username=staff_info['username'],
                defaults={
                    'first_name': staff_info['first_name'],
                    'last_name': staff_info['last_name'],
                    'email': staff_info['email'],
                    'role': staff_info['role']
                }
            )
            if created:
                user.set_password(staff_info['password'])
                user.save()

            staff, created = Staff.objects.get_or_create(
                user=user,
                defaults={
                    'department': staff_info['department'],
                    'position': staff_info['position'],
                    'data': {
                        'experience_years': staff_info['experience_years'],
                        'student_count': staff_info['student_count']
                    }
                }
            )
            self.stdout.write(f'Создан сотрудник: {user.get_full_name()}')

        # Создаем студентов
        students_data = [
            {
                'username': 'student1',
                'password': 'testpass123',
                'first_name': 'Алексей',
                'last_name': 'Смирнов',
                'email': 'smirnov@example.com',
                'role': 'student',
                'department': created_departments[0],
                'course': 1,
                'group': 'ИТ-101',
                'average_score': 4.8
            },
            {
                'username': 'student2',
                'password': 'testpass123',
                'first_name': 'Мария',
                'last_name': 'Козлова',
                'email': 'kozlova@example.com',
                'role': 'student',
                'department': created_departments[1],
                'course': 2,
                'group': 'БЭ-201',
                'average_score': 4.5
            },
            {
                'username': 'student3',
                'password': 'testpass123',
                'first_name': 'Дмитрий',
                'last_name': 'Новиков',
                'email': 'novikov@example.com',
                'role': 'student',
                'department': created_departments[2],
                'course': 3,
                'group': 'ИЯ-301',
                'average_score': 4.2
            }
        ]

        for student_info in students_data:
            user, created = User.objects.get_or_create(
                username=student_info['username'],
                defaults={
                    'first_name': student_info['first_name'],
                    'last_name': student_info['last_name'],
                    'email': student_info['email'],
                    'role': student_info['role']
                }
            )
            if created:
                user.set_password(student_info['password'])
                user.save()

            student, created = Student.objects.get_or_create(
                user=user,
                defaults={
                    'department': student_info['department'],
                    'course': student_info['course'],
                    'group': student_info['group'],
                    'data': {'average_score': student_info['average_score']}
                }
            )
            self.stdout.write(f'Создан студент: {user.get_full_name()}')

        self.stdout.write(self.style.SUCCESS('Тестовые данные успешно загружены!')) 