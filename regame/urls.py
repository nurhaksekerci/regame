from django.urls import path
from . import views

urlpatterns = [
    # Company URLs
    path('companies/', views.company_list, name='company_list'),
    path('companies/create/', views.create_company, name='create_company'),
    path('companies/<int:pk>/update/', views.update_company, name='update_company'),
    path('companies/<int:pk>/delete/', views.delete_company, name='delete_company'),
    
    # Presentation URLs
    path('companies/<int:company_id>/presentations/', views.presentation_list, name='presentation_list'),
    path('companies/<int:company_id>/presentations/create/', views.create_presentation, name='create_presentation'),
    path('companies/<int:company_id>/presentations/<int:pk>/update/', views.update_presentation, name='update_presentation'),
    path('companies/<int:company_id>/presentations/<int:pk>/delete/', views.delete_presentation, name='delete_presentation'),
    
    # Question URLs
    path('companies/<int:company_id>/presentations/<int:presentation_id>/questions/', views.question_list, name='question_list'),
    path('companies/<int:company_id>/presentations/<int:presentation_id>/questions/create/', views.create_question, name='create_question'),
    path('companies/<int:company_id>/presentations/<int:presentation_id>/questions/<int:question_number>/update/', views.update_question, name='update_question'),
    path('companies/<int:company_id>/presentations/<int:presentation_id>/questions/<int:question_number>/delete/', views.delete_question, name='delete_question'),
    
    # Classroom URLs
    path('classroom/select-company/', views.select_company_for_classroom, name='select_company_for_classroom'),
    path('classroom/<int:company_id>/select-presentation/', views.select_presentation_for_classroom, name='select_presentation_for_classroom'),
    path('classroom/<int:company_id>/<int:presentation_id>/create/', views.create_classroom, name='create_classroom'),
    path('classroom/<str:code>/', views.classroom_detail, name='classroom_detail'),
    path('classroom/<str:classroom_code>/update-info/', views.update_classroom_info, name='update_info'),
    
    # Participant URLs
    path('join/<str:code>/', views.join_classroom, name='join_classroom'),
    
    # Presentation View URLs
    path('presentation/<str:code>/', views.presentation_view, name='presentation_view'),
    
    # Anasayfa URLs
    path('', views.anasayfa, name='anasayfa'),  # Public anasayfa
    path('dashboard/', views.anasayfa2, name='dashboard'),  # Login gerektiren dashboard
    
    # Preview URL
    path('preview/<int:answer_id>/', views.preview_answer, name='preview_answer'),
    
    # Classroom Answers URL
    path('classroom/<str:code>/answers/', views.classroom_answers, name='classroom_answers'),
    
    # Trainer URLs
    path('trainers/', views.trainer_list, name='trainer_list'),
    path('trainers/<int:pk>/update/', views.update_trainer, name='update_trainer'),
]
