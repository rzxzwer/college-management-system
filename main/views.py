from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.urls import reverse_lazy
from .models import CustomUser, Department, Student, Staff, Statistics
from .forms import CustomUserCreationForm, StudentForm
from django.db.models import Count, Avg
from django.contrib.auth.models import User
from django.utils import timezone

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, 'Вы успешно вошли в систему!')
            return redirect('dashboard')
        else:
            messages.error(request, 'Неверное имя пользователя или пароль.')
    return render(request, 'main/login.html')

def logout_view(request):
    logout(request)
    messages.success(request, 'Вы успешно вышли из системы!')
    return redirect('home')

def home(request):
    return render(request, 'main/home.html')

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Регистрация успешна!')
            return redirect('dashboard')
    else:
        form = CustomUserCreationForm()
    return render(request, 'main/register.html', {'form': form})

@login_required
def dashboard(request):
    user = request.user
    if user.role == 'admin':
        context = {
            'total_students': Student.objects.count(),
            'total_teachers': Staff.objects.count(),
            'total_departments': Department.objects.count(),
            'average_score': 4.5,  # Здесь будет реальный расчет
            'department_labels': ['Отдел 1', 'Отдел 2', 'Отдел 3'],
            'department_scores': [4.2, 4.5, 4.8],
            'course_labels': ['1 курс', '2 курс', '3 курс', '4 курс'],
            'course_data': [100, 150, 120, 90],
            'recent_actions': [
                {'date': '2024-03-20', 'description': 'Добавлен новый студент', 'user': 'Admin', 'status': 'Успешно', 'status_color': 'success'},
                {'date': '2024-03-19', 'description': 'Обновлено расписание', 'user': 'Staff', 'status': 'В процессе', 'status_color': 'warning'},
            ]
        }
        return render(request, 'main/admin_dashboard.html', context)
    elif user.role == 'staff':
        context = {
            'my_groups': [
                {'name': 'Группа 1', 'students_count': 25, 'course': 1},
                {'name': 'Группа 2', 'students_count': 30, 'course': 2},
            ],
            'schedule': [
                {'time': '9:00-10:30', 'days': ['Математика', 'Физика', 'Химия', 'Биология', 'История', '']},
                {'time': '10:45-12:15', 'days': ['Физика', 'Математика', 'История', 'Химия', 'Биология', '']},
            ],
            'upcoming_events': [
                {'title': 'Экзамен по математике', 'date': '2024-03-25', 'description': 'Первый семестр'},
                {'title': 'Собрание преподавателей', 'date': '2024-03-26', 'description': 'Обсуждение учебного плана'},
            ],
            'group_labels': ['Группа 1', 'Группа 2'],
            'group_scores': [4.2, 4.5],
            'pending_documents': [
                {'student': 'Иванов И.И.', 'type': 'Заявление', 'submission_date': '2024-03-20', 'status': 'На рассмотрении', 'status_color': 'warning'},
            ]
        }
        return render(request, 'main/staff_dashboard.html', context)
    else:
        context = {
            'student': {
                'full_name': 'Иванов Иван Иванович',
                'group': 'Группа 1',
                'course': 1,
                'average_score': 4.5
            },
            'schedule': [
                {'time': '9:00-10:30', 'days': ['Математика', 'Физика', 'Химия', 'Биология', 'История', '']},
                {'time': '10:45-12:15', 'days': ['Физика', 'Математика', 'История', 'Химия', 'Биология', '']},
            ],
            'upcoming_events': [
                {'title': 'Экзамен по математике', 'date': '2024-03-25', 'description': 'Первый семестр'},
                {'title': 'Собрание группы', 'date': '2024-03-26', 'description': 'Обсуждение учебного плана'},
            ],
            'subject_labels': ['Математика', 'Физика', 'Химия', 'Биология', 'История'],
            'subject_grades': [4, 5, 4, 5, 4],
            'my_documents': [
                {'type': 'Заявление', 'submission_date': '2024-03-20', 'status': 'Принято', 'status_color': 'success'},
            ]
        }
        return render(request, 'main/student_dashboard.html', context)

class DepartmentListView(LoginRequiredMixin, ListView):
    model = Department
    template_name = 'main/department_list.html'
    context_object_name = 'departments'

    def get_queryset(self):
        # Создаем тестовые отделы, если их нет
        departments_data = [
            {
                'name': 'Информационные технологии',
                'description': 'Отдел, отвечающий за IT-направления'
            },
            {
                'name': 'Экономика и управление',
                'description': 'Подготовка экономистов и менеджеров'
            },
            {
                'name': 'Иностранные языки',
                'description': 'Изучение иностранных языков'
            }
        ]
        
        departments = []
        for dept_data in departments_data:
            dept, created = Department.objects.get_or_create(
                name=dept_data['name'],
                defaults={'data': {'description': dept_data['description']}}
            )
            departments.append(dept)
        
        return Department.objects.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        for department in context['departments']:
            department.student_count = Student.objects.filter(department=department).count()
            department.staff_count = Staff.objects.filter(department=department).count()
        return context

class DepartmentDetailView(LoginRequiredMixin, DetailView):
    model = Department
    template_name = 'main/department_detail.html'
    context_object_name = 'department'

class StudentListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = Student
    template_name = 'main/student_list.html'
    context_object_name = 'students'
    ordering = ['user__last_name', 'user__first_name']

    def test_func(self):
        return self.request.user.role in ['admin', 'staff']

    def get_queryset(self):
        # Создаем тестовых студентов, если их нет
        if Student.objects.count() == 0:
            departments = Department.objects.all()
            if departments.exists():
                student_data = [
                    # ИТ отдел - 1 курс
                    {'first_name': 'Тимур', 'last_name': 'Коняшкин', 'group': 'ИТ-101', 'course': 1, 'department': departments[0], 'average_score': 4.8},
                    {'first_name': 'Мария', 'last_name': 'Смирнова', 'group': 'ИТ-101', 'course': 1, 'department': departments[0], 'average_score': 4.6},
                    {'first_name': 'Александр', 'last_name': 'Петров', 'group': 'ИТ-101', 'course': 1, 'department': departments[0], 'average_score': 4.3},
                    {'first_name': 'Екатерина', 'last_name': 'Козлова', 'group': 'ИТ-101', 'course': 1, 'department': departments[0], 'average_score': 4.7},
                    {'first_name': 'Дмитрий', 'last_name': 'Соколов', 'group': 'ИТ-102', 'course': 1, 'department': departments[0], 'average_score': 4.4},
                    {'first_name': 'Анна', 'last_name': 'Морозова', 'group': 'ИТ-102', 'course': 1, 'department': departments[0], 'average_score': 4.9},
                    {'first_name': 'Павел', 'last_name': 'Волков', 'group': 'ИТ-102', 'course': 1, 'department': departments[0], 'average_score': 4.5},
                    {'first_name': 'Ольга', 'last_name': 'Новикова', 'group': 'ИТ-102', 'course': 1, 'department': departments[0], 'average_score': 4.2},
                    {'first_name': 'Сергей', 'last_name': 'Кузнецов', 'group': 'ИТ-103', 'course': 1, 'department': departments[0], 'average_score': 4.6},
                    {'first_name': 'Татьяна', 'last_name': 'Федорова', 'group': 'ИТ-103', 'course': 1, 'department': departments[0], 'average_score': 4.8},
                    
                    # ИТ отдел - 2 курс
                    {'first_name': 'Андрей', 'last_name': 'Михайлов', 'group': 'ИТ-201', 'course': 2, 'department': departments[0], 'average_score': 4.3},
                    {'first_name': 'Наталья', 'last_name': 'Егорова', 'group': 'ИТ-201', 'course': 2, 'department': departments[0], 'average_score': 4.7},
                    {'first_name': 'Максим', 'last_name': 'Орлов', 'group': 'ИТ-201', 'course': 2, 'department': departments[0], 'average_score': 4.4},
                    {'first_name': 'Юлия', 'last_name': 'Антонова', 'group': 'ИТ-201', 'course': 2, 'department': departments[0], 'average_score': 4.9},
                    {'first_name': 'Артем', 'last_name': 'Соловьев', 'group': 'ИТ-202', 'course': 2, 'department': departments[0], 'average_score': 4.5},
                    {'first_name': 'Евгения', 'last_name': 'Белова', 'group': 'ИТ-202', 'course': 2, 'department': departments[0], 'average_score': 4.7},
                    {'first_name': 'Игорь', 'last_name': 'Медведев', 'group': 'ИТ-202', 'course': 2, 'department': departments[0], 'average_score': 4.4},
                    {'first_name': 'Светлана', 'last_name': 'Гаврилова', 'group': 'ИТ-202', 'course': 2, 'department': departments[0], 'average_score': 4.8},
                    
                    # Экономика - 1 курс
                    {'first_name': 'Роман', 'last_name': 'Тихонов', 'group': 'ЭК-101', 'course': 1, 'department': departments[1], 'average_score': 4.6},
                    {'first_name': 'Алина', 'last_name': 'Комарова', 'group': 'ЭК-101', 'course': 1, 'department': departments[1], 'average_score': 4.9},
                    {'first_name': 'Денис', 'last_name': 'Зайцев', 'group': 'ЭК-101', 'course': 1, 'department': departments[1], 'average_score': 4.5},
                    {'first_name': 'Марина', 'last_name': 'Котова', 'group': 'ЭК-101', 'course': 1, 'department': departments[1], 'average_score': 4.7},
                    {'first_name': 'Виктор', 'last_name': 'Лебедев', 'group': 'ЭК-102', 'course': 1, 'department': departments[1], 'average_score': 4.3},
                    {'first_name': 'Алексей', 'last_name': 'Сидоров', 'group': 'ЭК-102', 'course': 1, 'department': departments[1], 'average_score': 4.8},
                    {'first_name': 'Елена', 'last_name': 'Попова', 'group': 'ЭК-102', 'course': 1, 'department': departments[1], 'average_score': 4.6},
                    {'first_name': 'Дмитрий', 'last_name': 'Васильев', 'group': 'ЭК-102', 'course': 1, 'department': departments[1], 'average_score': 4.4},
                    {'first_name': 'Анна', 'last_name': 'Соколова', 'group': 'ЭК-103', 'course': 1, 'department': departments[1], 'average_score': 4.7},
                    {'first_name': 'Иван', 'last_name': 'Морозов', 'group': 'ЭК-103', 'course': 1, 'department': departments[1], 'average_score': 4.5},
                    
                    # Экономика - 2 курс
                    {'first_name': 'Мария', 'last_name': 'Новикова', 'group': 'ЭК-201', 'course': 2, 'department': departments[1], 'average_score': 4.8},
                    {'first_name': 'Петр', 'last_name': 'Волков', 'group': 'ЭК-201', 'course': 2, 'department': departments[1], 'average_score': 4.6},
                    {'first_name': 'Ольга', 'last_name': 'Козлова', 'group': 'ЭК-201', 'course': 2, 'department': departments[1], 'average_score': 4.9},
                    {'first_name': 'Сергей', 'last_name': 'Смирнов', 'group': 'ЭК-201', 'course': 2, 'department': departments[1], 'average_score': 4.4},
                    {'first_name': 'Татьяна', 'last_name': 'Петрова', 'group': 'ЭК-202', 'course': 2, 'department': departments[1], 'average_score': 4.7},
                    {'first_name': 'Андрей', 'last_name': 'Соколов', 'group': 'ЭК-202', 'course': 2, 'department': departments[1], 'average_score': 4.5},
                    {'first_name': 'Наталья', 'last_name': 'Лебедева', 'group': 'ЭК-202', 'course': 2, 'department': departments[1], 'average_score': 4.8},
                    {'first_name': 'Максим', 'last_name': 'Кузнецов', 'group': 'ЭК-202', 'course': 2, 'department': departments[1], 'average_score': 4.3},
                    
                    # Иностранные языки - 1 курс
                    {'first_name': 'Юлия', 'last_name': 'Попова', 'group': 'ИЯ-101', 'course': 1, 'department': departments[2], 'average_score': 4.9},
                    {'first_name': 'Артем', 'last_name': 'Васильев', 'group': 'ИЯ-101', 'course': 1, 'department': departments[2], 'average_score': 4.6},
                    {'first_name': 'Евгения', 'last_name': 'Соколова', 'group': 'ИЯ-101', 'course': 1, 'department': departments[2], 'average_score': 4.8},
                    {'first_name': 'Игорь', 'last_name': 'Морозов', 'group': 'ИЯ-101', 'course': 1, 'department': departments[2], 'average_score': 4.5},
                    {'first_name': 'Светлана', 'last_name': 'Новикова', 'group': 'ИЯ-102', 'course': 1, 'department': departments[2], 'average_score': 4.7},
                    {'first_name': 'Роман', 'last_name': 'Волков', 'group': 'ИЯ-102', 'course': 1, 'department': departments[2], 'average_score': 4.4},
                    {'first_name': 'Алина', 'last_name': 'Козлова', 'group': 'ИЯ-102', 'course': 1, 'department': departments[2], 'average_score': 4.9},
                    {'first_name': 'Денис', 'last_name': 'Смирнов', 'group': 'ИЯ-102', 'course': 1, 'department': departments[2], 'average_score': 4.6},
                    {'first_name': 'Марина', 'last_name': 'Петрова', 'group': 'ИЯ-103', 'course': 1, 'department': departments[2], 'average_score': 4.8},
                    {'first_name': 'Виктор', 'last_name': 'Соколов', 'group': 'ИЯ-103', 'course': 1, 'department': departments[2], 'average_score': 4.5},
                    
                    # Иностранные языки - 2 курс
                    {'first_name': 'Алексей', 'last_name': 'Лебедев', 'group': 'ИЯ-201', 'course': 2, 'department': departments[2], 'average_score': 4.7},
                    {'first_name': 'Елена', 'last_name': 'Кузнецова', 'group': 'ИЯ-201', 'course': 2, 'department': departments[2], 'average_score': 4.4},
                    {'first_name': 'Дмитрий', 'last_name': 'Попов', 'group': 'ИЯ-201', 'course': 2, 'department': departments[2], 'average_score': 4.9},
                    {'first_name': 'Анна', 'last_name': 'Васильева', 'group': 'ИЯ-201', 'course': 2, 'department': departments[2], 'average_score': 4.6},
                    {'first_name': 'Иван', 'last_name': 'Соколов', 'group': 'ИЯ-202', 'course': 2, 'department': departments[2], 'average_score': 4.8},
                    {'first_name': 'Мария', 'last_name': 'Морозова', 'group': 'ИЯ-202', 'course': 2, 'department': departments[2], 'average_score': 4.5},
                    {'first_name': 'Петр', 'last_name': 'Новиков', 'group': 'ИЯ-202', 'course': 2, 'department': departments[2], 'average_score': 4.7},
                    {'first_name': 'Ольга', 'last_name': 'Волкова', 'group': 'ИЯ-202', 'course': 2, 'department': departments[2], 'average_score': 4.4}
                ]

                for data in student_data:
                    user, created = CustomUser.objects.get_or_create(
                        username=f"{data['last_name'].lower()}_{data['first_name'].lower()}",
                        defaults={
                            'first_name': data['first_name'],
                            'last_name': data['last_name'],
                            'role': 'student'
                        }
                    )
                    if created:
                        user.set_password('testpass123')
                        user.save()
                    
                    Student.objects.get_or_create(
                        user=user,
                        defaults={
                            'department': data['department'],
                            'course': data['course'],
                            'group': data['group'],
                            'data': {'average_score': data['average_score']}
                        }
                    )

        return Student.objects.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        for student in context['students']:
            student.average_score = student.data.get('average_score', 0)
        return context

class StaffListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = Staff
    template_name = 'main/staff_list.html'
    context_object_name = 'staff'
    ordering = ['user__last_name', 'user__first_name']

    def test_func(self):
        return self.request.user.role in ['admin', 'staff']

    def get_queryset(self):
        # Создаем тестовый персонал, если его нет
        if Staff.objects.count() == 0:
            departments = Department.objects.all()
            if departments.exists():
                staff_data = [
                    # ИТ отдел
                    {
                        'first_name': 'Петр',
                        'last_name': 'Петров',
                        'position': 'Заведующий кафедрой',
                        'department': departments[0],
                        'experience_years': 15,
                        'student_count': 60
                    },
                    {
                        'first_name': 'Елена',
                        'last_name': 'Сидорова',
                        'position': 'Профессор',
                        'department': departments[0],
                        'experience_years': 12,
                        'student_count': 45
                    },
                    {
                        'first_name': 'Андрей',
                        'last_name': 'Козлов',
                        'position': 'Доцент',
                        'department': departments[0],
                        'experience_years': 8,
                        'student_count': 30
                    },
                    {
                        'first_name': 'Ирина',
                        'last_name': 'Волкова',
                        'position': 'Старший преподаватель',
                        'department': departments[0],
                        'experience_years': 6,
                        'student_count': 25
                    },

                    # Экономика
                    {
                        'first_name': 'Михаил',
                        'last_name': 'Соколов',
                        'position': 'Заведующий кафедрой',
                        'department': departments[1],
                        'experience_years': 18,
                        'student_count': 65
                    },
                    {
                        'first_name': 'Наталья',
                        'last_name': 'Морозова',
                        'position': 'Профессор',
                        'department': departments[1],
                        'experience_years': 14,
                        'student_count': 50
                    },
                    {
                        'first_name': 'Сергей',
                        'last_name': 'Лебедев',
                        'position': 'Доцент',
                        'department': departments[1],
                        'experience_years': 9,
                        'student_count': 35
                    },
                    {
                        'first_name': 'Ольга',
                        'last_name': 'Кузнецова',
                        'position': 'Старший преподаватель',
                        'department': departments[1],
                        'experience_years': 7,
                        'student_count': 28
                    },

                    # Иностранные языки
                    {
                        'first_name': 'Александр',
                        'last_name': 'Новиков',
                        'position': 'Заведующий кафедрой',
                        'department': departments[2],
                        'experience_years': 16,
                        'student_count': 55
                    },
                    {
                        'first_name': 'Татьяна',
                        'last_name': 'Федорова',
                        'position': 'Профессор',
                        'department': departments[2],
                        'experience_years': 13,
                        'student_count': 48
                    },
                    {
                        'first_name': 'Дмитрий',
                        'last_name': 'Попов',
                        'position': 'Доцент',
                        'department': departments[2],
                        'experience_years': 10,
                        'student_count': 40
                    },
                    {
                        'first_name': 'Анна',
                        'last_name': 'Смирнова',
                        'position': 'Старший преподаватель',
                        'department': departments[2],
                        'experience_years': 5,
                        'student_count': 22
                    }
                ]

                for data in staff_data:
                    user, created = CustomUser.objects.get_or_create(
                        username=f"{data['last_name'].lower()}_{data['first_name'].lower()}",
                        defaults={
                            'first_name': data['first_name'],
                            'last_name': data['last_name'],
                            'role': 'staff'
                        }
                    )
                    if created:
                        user.set_password('testpass123')
                        user.save()
                    
                    Staff.objects.get_or_create(
                        user=user,
                        defaults={
                            'department': data['department'],
                            'position': data['position'],
                            'data': {
                                'experience_years': data['experience_years'],
                                'student_count': data['student_count']
                            }
                        }
                    )

        return Staff.objects.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        for staff_member in context['staff']:
            staff_member.experience_years = staff_member.data.get('experience_years', 0)
            staff_member.student_count = staff_member.data.get('student_count', 0)
        return context

@login_required
def statistics_view(request):
    return render(request, 'main/statistics.html')

class StudentDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    model = Student
    template_name = 'main/student_detail.html'
    context_object_name = 'student'

    def test_func(self):
        return self.request.user.is_staff

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

class StudentCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Student
    form_class = StudentForm
    template_name = 'main/student_form.html'
    success_url = reverse_lazy('student_list')

    def test_func(self):
        return self.request.user.is_staff

    def form_valid(self, form):
        # Создаем пользователя для студента
        user = User.objects.create_user(
            username=form.cleaned_data['username'],
            password=form.cleaned_data['password'],
            first_name=form.cleaned_data['first_name'],
            last_name=form.cleaned_data['last_name'],
            email=form.cleaned_data['email']
        )
        form.instance.user = user
        return super().form_valid(form)

class StudentUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Student
    form_class = StudentForm
    template_name = 'main/student_form.html'
    success_url = reverse_lazy('student_list')

    def test_func(self):
        return self.request.user.is_staff

    def form_valid(self, form):
        if form.cleaned_data.get('password'):
            self.object.user.set_password(form.cleaned_data['password'])
            self.object.user.save()
        return super().form_valid(form)

class StudentDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Student
    template_name = 'main/student_confirm_delete.html'
    success_url = reverse_lazy('student_list')

    def test_func(self):
        return self.request.user.is_staff

    def delete(self, request, *args, **kwargs):
        student = self.get_object()
        student.user.delete()
        return super().delete(request, *args, **kwargs)

@login_required
def student_documents(request):
    if not hasattr(request.user, 'student'):
        messages.error(request, 'У вас нет доступа к этой странице.')
        return redirect('home')
    
    documents = Document.objects.filter(student=request.user.student)
    return render(request, 'main/student_documents.html', {'documents': documents})

@login_required
def document_upload(request):
    if not hasattr(request.user, 'student'):
        messages.error(request, 'У вас нет доступа к этой странице.')
        return redirect('home')
    
    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            document = form.save(commit=False)
            document.student = request.user.student
            document.save()
            messages.success(request, 'Документ успешно загружен.')
            return redirect('student_documents')
    else:
        form = DocumentForm()
    
    return render(request, 'main/document_upload.html', {'form': form})

@login_required
def document_detail(request, pk):
    document = get_object_or_404(Document, pk=pk)
    
    # Проверяем права доступа
    if not (hasattr(request.user, 'staff') or document.student == request.user.student):
        messages.error(request, 'У вас нет доступа к этому документу.')
        return redirect('home')
    
    return render(request, 'main/document_detail.html', {'document': document})

@login_required
def document_process(request, pk):
    if not hasattr(request.user, 'staff'):
        messages.error(request, 'У вас нет доступа к этой странице.')
        return redirect('home')
    
    document = get_object_or_404(Document, pk=pk)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        rejection_reason = request.POST.get('rejection_reason', '')
        
        if action == 'approve':
            document.status = 'approved'
            document.processed_at = timezone.now()
            document.processed_by = request.user
            document.save()
            messages.success(request, 'Документ одобрен.')
        elif action == 'reject':
            document.status = 'rejected'
            document.processed_at = timezone.now()
            document.processed_by = request.user
            document.rejection_reason = rejection_reason
            document.save()
            messages.success(request, 'Документ отклонен.')
        
        return redirect('document_detail', pk=pk)
    
    return render(request, 'main/document_process.html', {'document': document})

@login_required
def student_schedule(request):
    if not hasattr(request.user, 'student'):
        messages.error(request, 'У вас нет доступа к этой странице.')
        return redirect('home')
    return render(request, 'main/student_schedule.html')

@login_required
def student_grades(request):
    if not hasattr(request.user, 'student'):
        messages.error(request, 'У вас нет доступа к этой странице.')
        return redirect('home')
    return render(request, 'main/student_grades.html')

@login_required
def student_attendance(request):
    if not hasattr(request.user, 'student'):
        messages.error(request, 'У вас нет доступа к этой странице.')
        return redirect('home')
    return render(request, 'main/student_attendance.html')

@login_required
def student_profile(request):
    if not hasattr(request.user, 'student'):
        messages.error(request, 'У вас нет доступа к этой странице.')
        return redirect('home')
    return render(request, 'main/student_profile.html')
