from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Company, Presentation, Classroom, Participant, Answer, User
from django.contrib.auth.decorators import login_required
import json
import qrcode
from io import BytesIO
from django.core.files.base import ContentFile
import random
import string
from django.db.models import Count

@login_required
def company_list(request):
    companies = Company.objects.all().order_by('-is_active', '-created_at')
    company_data = []
    
    for company in companies:
        company_data.append({
            'id': company.id,
            'values': [
                company.name, 
                company.logo.url if company.logo else '', 
                company.created_at.strftime('%d/%m/%Y %H:%M'), 
                'Aktif' if company.is_active else 'Pasif'
            ],
            'is_active': company.is_active
        })
    
    context = {
        'companies': company_data,
        'title': 'Şirketler'
    }
    return render(request, 'regame/company/list.html', context)

@login_required
def create_company(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        logo = request.FILES.get('logo')
        
        company = Company.objects.create(
            name=name,
            logo=logo
        )
        messages.success(request, 'Şirket başarıyla oluşturuldu.')
        return redirect('company_list')
    
    return render(request, 'regame/company/create.html', {'title': 'Şirket Oluştur'})

@login_required
def update_company(request, pk):
    company = get_object_or_404(Company, pk=pk)
    
    if request.method == 'POST':
        company.name = request.POST.get('name')
        if request.FILES.get('logo'):
            company.logo = request.FILES.get('logo')
        company.save()
        
        messages.success(request, 'Şirket başarıyla güncellendi.')
        return redirect('company_list')
    
    context = {
        'company': company,
        'title': 'Şirket Güncelle'
    }
    return render(request, 'regame/company/update.html', context)

@login_required
def delete_company(request, pk):
    company = get_object_or_404(Company, pk=pk)
    company.is_active = not company.is_active
    company.save()
    
    company_data = {
        'id': company.id,
        'values': [
            company.name, 
            company.logo.url if company.logo else '', 
            company.created_at.strftime('%d/%m/%Y %H:%M'), 
            'Aktif' if company.is_active else 'Pasif'
        ],
        'is_active': company.is_active
    }
    
    messages.success(
        request, 
        f'Şirket başarıyla {"aktifleştirildi" if company.is_active else "pasifleştirildi"}.'
    )
    
    return redirect('company_list')

@login_required
def presentation_list(request, company_id):
    company = get_object_or_404(Company, id=company_id)
    presentations = Presentation.objects.filter(company=company).order_by('-is_active', '-created_at')
    presentation_data = []
    
    for presentation in presentations:
        presentation_data.append({
            'id': presentation.id,
            'values': [
                presentation.name,
                presentation.bg_image.url if presentation.bg_image else '',
                presentation.created_at.strftime('%d/%m/%Y %H:%M'),
                'Aktif' if presentation.is_active else 'Pasif'
            ],
            'is_active': presentation.is_active
        })
    
    context = {
        'presentations': presentation_data,
        'company': company,
        'title': f'{company.name} - Sunumlar'
    }
    return render(request, 'regame/presentation/list.html', context)

@login_required
def create_presentation(request, company_id):
    company = get_object_or_404(Company, id=company_id)
    
    if request.method == 'POST':
        name = request.POST.get('name')
        bg_image = request.FILES.get('bg_image')
        
        presentation = Presentation.objects.create(
            company=company,
            name=name,
            bg_image=bg_image,
            questions=[]  # Boş soru listesi ile başlat
        )
        messages.success(request, 'Sunum başarıyla oluşturuldu.')
        return redirect('presentation_list', company_id=company.id)
    
    return render(request, 'regame/presentation/create.html', {
        'company': company,
        'title': f'{company.name} - Yeni Sunum'
    })

@login_required
def update_presentation(request, company_id, pk):
    company = get_object_or_404(Company, id=company_id)
    presentation = get_object_or_404(Presentation, pk=pk, company=company)
    
    if request.method == 'POST':
        presentation.name = request.POST.get('name')
        if request.FILES.get('bg_image'):
            presentation.bg_image = request.FILES.get('bg_image')
        presentation.save()
        
        messages.success(request, 'Sunum başarıyla güncellendi.')
        return redirect('presentation_list', company_id=company.id)
    
    context = {
        'presentation': presentation,
        'company': company,
        'title': f'{company.name} - Sunum Güncelle'
    }
    return render(request, 'regame/presentation/update.html', context)

@login_required
def delete_presentation(request, company_id, pk):
    company = get_object_or_404(Company, id=company_id)
    presentation = get_object_or_404(Presentation, pk=pk, company=company)
    presentation.is_active = not presentation.is_active
    presentation.save()
    
    messages.success(
        request, 
        f'Sunum başarıyla {"aktifleştirildi" if presentation.is_active else "pasifleştirildi"}.'
    )
    
    return redirect('presentation_list', company_id=company.id)

@login_required
def question_list(request, company_id, presentation_id):
    company = get_object_or_404(Company, id=company_id)
    presentation = get_object_or_404(Presentation, id=presentation_id, company=company)
    
    # Mevcut soruları al ve sıralı göster
    questions = presentation.questions or []
    questions.sort(key=lambda x: x.get('question_number', 0))
    
    context = {
        'company': company,
        'presentation': presentation,
        'questions': questions,
        'title': f'{presentation.name} - Sorular'
    }
    return render(request, 'regame/question/list.html', context)

@login_required
def create_question(request, company_id, presentation_id):
    company = get_object_or_404(Company, id=company_id)
    presentation = get_object_or_404(Presentation, id=presentation_id, company=company)
    
    if request.method == 'POST':
        question_number = int(request.POST.get('question_number', 0))
        question_text = request.POST.get('question_text', '')
        
        # Mevcut soruları al veya boş liste oluştur
        questions = presentation.questions or []
        
        # Yeni soruyu ekle
        questions.append({
            'question_number': question_number,
            'question_text': question_text
        })
        
        # Soruları soru numarasına göre sırala
        questions.sort(key=lambda x: x['question_number'])
        
        # Sunumu güncelle
        presentation.questions = questions
        presentation.save()
        
        messages.success(request, 'Soru başarıyla eklendi.')
        return redirect('question_list', company_id=company.id, presentation_id=presentation.id)
    
    context = {
        'company': company,
        'presentation': presentation,
        'title': f'{presentation.name} - Yeni Soru'
    }
    return render(request, 'regame/question/create.html', context)

@login_required
def update_question(request, company_id, presentation_id, question_number):
    company = get_object_or_404(Company, id=company_id)
    presentation = get_object_or_404(Presentation, id=presentation_id, company=company)
    
    # Mevcut soruları al
    questions = presentation.questions or []
    
    # İlgili soruyu bul
    question = next((q for q in questions if q['question_number'] == int(question_number)), None)
    if not question:
        messages.error(request, 'Soru bulunamadı.')
        return redirect('question_list', company_id=company.id, presentation_id=presentation.id)
    
    if request.method == 'POST':
        new_question_number = int(request.POST.get('question_number', 0))
        question_text = request.POST.get('question_text', '')
        
        # Soruyu güncelle
        questions.remove(question)
        questions.append({
            'question_number': new_question_number,
            'question_text': question_text
        })
        
        # Soruları sırala
        questions.sort(key=lambda x: x['question_number'])
        
        # Sunumu güncelle
        presentation.questions = questions
        presentation.save()
        
        messages.success(request, 'Soru başarıyla güncellendi.')
        return redirect('question_list', company_id=company.id, presentation_id=presentation.id)
    
    context = {
        'company': company,
        'presentation': presentation,
        'question': question,
        'title': f'{presentation.name} - Soru Güncelle'
    }
    return render(request, 'regame/question/update.html', context)

@login_required
def delete_question(request, company_id, presentation_id, question_number):
    company = get_object_or_404(Company, id=company_id)
    presentation = get_object_or_404(Presentation, id=presentation_id, company=company)
    
    # Mevcut soruları al
    questions = presentation.questions or []
    
    # İlgili soruyu bul ve sil
    question = next((q for q in questions if q['question_number'] == int(question_number)), None)
    if question:
        questions.remove(question)
        
        # Sunumu güncelle
        presentation.questions = questions
        presentation.save()
        
        messages.success(request, 'Soru başarıyla silindi.')
    else:
        messages.error(request, 'Soru bulunamadı.')
    
    return redirect('question_list', company_id=company.id, presentation_id=presentation.id)

def generate_class_code():
    """6 karakterli rastgele alfanumerik kod üretir"""
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

def generate_qr_code(url):
    """Verilen URL için QR kod oluşturur"""
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(url)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    
    return ContentFile(buffer.getvalue())

@login_required
def select_company_for_classroom(request):
    companies = Company.objects.filter(is_active=True)
    return render(request, 'regame/classroom/select_company.html', {
        'companies': companies,
        'title': 'Şirket Seç'
    })

@login_required
def select_presentation_for_classroom(request, company_id):
    company = get_object_or_404(Company, id=company_id)
    presentations = Presentation.objects.filter(company=company, is_active=True)
    
    return render(request, 'regame/classroom/select_presentation.html', {
        'company': company,
        'presentations': presentations,
        'title': f'{company.name} - Sunum Seç'
    })

@login_required
def create_classroom(request, company_id, presentation_id):
    company = get_object_or_404(Company, id=company_id)
    presentation = get_object_or_404(Presentation, id=presentation_id, company=company)
    
    if request.method == 'POST':
        # Benzersiz kod üret
        while True:
            code = generate_class_code()
            if not Classroom.objects.filter(code=code).exists():
                break
        
        # Sınıfı oluştur
        classroom = Classroom.objects.create(
            company=company,
            presentation=presentation,
            code=code
        )
        
        # QR kod için URL oluştur - join URL'ine yönlendir
        url = request.build_absolute_uri(f'/join/{code}/')
        
        # QR kodu oluştur ve kaydet
        qr_image = generate_qr_code(url)
        classroom.qr_image.save(f'qr_{code}.png', qr_image, save=True)
        
        messages.success(request, 'Sınıf başarıyla oluşturuldu.')
        return redirect('classroom_detail', code=code)
    
    return render(request, 'regame/classroom/create.html', {
        'company': company,
        'presentation': presentation,
        'title': 'Sınıf Oluştur'
    })

@login_required
def classroom_detail(request, code):
    classroom = get_object_or_404(Classroom, code=code)
    
    # Sınıfı aktifleştirme/pasifleştirme işlemi
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'toggle_active':
            classroom.is_active = not classroom.is_active
            classroom.save()
            status = 'aktifleştirildi' if classroom.is_active else 'pasifleştirildi'
            messages.success(request, f'Sınıf başarıyla {status}.')
            return redirect('classroom_detail', code=code)
    
    context = {
        'classroom': classroom,
        'title': f'Sınıf: {code}',
        'toplam': classroom.participants.count(),
        'bitiren': classroom.answers.count()
    }
    return render(request, 'pages/classroom.html', context)

# HTMX için katılımcı bilgilerini güncelleyen view
def update_classroom_info(request, classroom_code):
    classroom = get_object_or_404(Classroom, code=classroom_code)
    context = {
        'toplam': classroom.participants.count(),
        'bitiren': classroom.answers.count()
    }
    return render(request, 'includes/classroom_info.html', context)

def join_classroom(request, code):
    classroom = get_object_or_404(Classroom, code=code)
    
    # Sınıf aktif değilse katılıma izin verme
    if not classroom.is_active:
        messages.error(request, 'Katılmak istediğiniz sınıf aktif değil.')
        return redirect('anasayfa')
    
    if request.method == 'POST':
        email = request.POST.get('email')
        name = request.POST.get('name')
        office = request.POST.get('office')
        
        # E-posta ile katılımcıyı kontrol et
        participant, created = Participant.objects.get_or_create(
            email=email,
            defaults={
                'name': name,
                'office': office,
                'company': classroom.company
            }
        )
        
        # Katılımcıyı sınıfa ekle
        if participant not in classroom.participants.all():
            classroom.participants.add(participant)
            messages.success(request, 'Sunuma başarıyla katıldınız!')
        else:
            messages.info(request, 'Zaten bu sunuma katılmışsınız.')
        
        # Email'i session'a kaydet
        request.session['participant_email'] = email
        
        return redirect('presentation_view', code=code)
    
    return render(request, 'regame/classroom/join.html', {
        'classroom': classroom,
        'title': 'Seni Tanıyor Muyuz?'
    })

def presentation_view(request, code):
    classroom = get_object_or_404(Classroom, code=code)
    presentation = classroom.presentation
    participant = None
    
    # Katılımcıyı bul
    if request.session.get('participant_email'):
        participant = get_object_or_404(
            Participant, 
            email=request.session['participant_email']
        )
        
        # Daha önce cevap vermiş mi kontrol et
        existing_answer = Answer.objects.filter(
            participant=participant,
            presentation=presentation,
            classroom=classroom
        ).first()
        
        if existing_answer:
            messages.info(request, 'Bu sunuma daha önce katıldınız.')
            return render(request, 'pages/preview.html', {
                'classroom': classroom,
                'presentation': presentation,
                'participant': participant,
                'answers': existing_answer.answers
            })
    
    if request.method == 'POST':
        answers_json = request.POST.get('answers')  # JSON string olarak gelecek
        try:
            answers_data = json.loads(answers_json)
            
            # Her cevap için soru metnini de ekle
            formatted_answers = []
            for answer in answers_data:
                question = next(
                    (q for q in presentation.questions if q['question_number'] == answer['question_number']), 
                    None
                )
                if question:
                    formatted_answers.append({
                        'question_number': answer['question_number'],
                        'question_text': question['question_text'],
                        'answer_text': answer['answer_text']
                    })
            
            # Tüm cevapları tek seferde kaydet
            Answer.objects.create(
                participant=participant,
                presentation=presentation,
                classroom=classroom,
                answers=formatted_answers
            )
            
            messages.success(request, 'Cevaplarınız başarıyla kaydedildi.')
            return render(request, 'pages/preview.html', {
                'classroom': classroom,
                'presentation': presentation,
                'participant': participant,
                'answers': formatted_answers
            })
            
        except json.JSONDecodeError:
            messages.error(request, 'Cevaplar geçerli formatta değil.')
    
    return render(request, 'pages/soru.html', {
        'classroom': classroom,
        'presentation': presentation,
        'questions': presentation.questions
    })

def anasayfa(request):
    # POST isteği gelirse (sınıf koduna katılma isteği)
    if request.method == 'POST':
        code = request.POST.get('code')
        if code:
            return redirect('join_classroom', code=code)
    
    # İstatistikleri hesapla
    context = {
        'company_count': Company.objects.filter(is_active=True).count(),
        'office_count': Participant.objects.values('office').distinct().count(),
        'participant_count': Participant.objects.filter(is_active=True).count(),
    }
    
    return render(request, 'pages/anasayfa.html', context)

@login_required
def anasayfa2(request):
    # POST isteği gelirse (email ile arama)
    if request.method == 'POST':
        email = request.POST.get('email')
        participant = None
        answers = []
        
        if email:
            participant = Participant.objects.filter(email=email).first()
            if participant:
                answers = Answer.objects.filter(
                    participant=participant,
                    is_active=True
                ).select_related('presentation', 'classroom')
    else:
        participant = None
        answers = []
    
    # Tüm sınıfları getir (aktif/pasif)
    classrooms = Classroom.objects.select_related(
        'company', 
        'presentation'
    ).prefetch_related(
        'participants',
        'answers'
    ).order_by('-created_at')  # En son oluşturulan en üstte
    
    context = {
        'company_count': Company.objects.filter(is_active=True).count(),
        'office_count': Participant.objects.values('office').distinct().count(),
        'participant_count': Participant.objects.filter(is_active=True).count(),
        'participant': participant,
        'answers': answers,
        'classrooms': classrooms
    }
    
    return render(request, 'pages/anasayfa2.html', context)

@login_required
def preview_answer(request, answer_id):
    answer = get_object_or_404(Answer, id=answer_id)
    
    context = {
        'classroom': answer.classroom,
        'presentation': answer.presentation,
        'participant': answer.participant,
        'answers': answer.answers
    }
    
    return render(request, 'pages/preview.html', context)

@login_required
def classroom_answers(request, code):
    classroom = get_object_or_404(Classroom.objects.select_related(
        'company', 
        'presentation'
    ), code=code)
    
    # Sınıftaki tüm cevapları getir
    answers = Answer.objects.filter(
        classroom=classroom
    ).select_related(
        'participant',
        'presentation'
    ).order_by('-created_at')
    
    context = {
        'classroom': classroom,
        'answers': answers,
        'participant_count': classroom.participants.count(),
        'answer_count': answers.count()
    }
    
    return render(request, 'pages/classroom_answers.html', context)

@login_required
def classroom_view(request, code):
    classroom = get_object_or_404(Classroom, code=code)
    
    context = {
        'classroom': classroom,
        'title': f'Sınıf: {code}',
        'toplam': classroom.participants.count(),
        'bitiren': classroom.answers.count()
    }
    return render(request, 'pages/classroom.html', context)

@login_required
def trainer_list(request):
    # Sadece is_staff=True olan kullanıcıları getir
    trainers = User.objects.filter(is_staff=True).order_by('-date_joined')
    
    trainer_data = []
    for trainer in trainers:
        trainer_data.append({
            'id': trainer.id,
            'values': [
                f"{trainer.first_name} {trainer.last_name}",
                trainer.email,
                trainer.date_joined.strftime('%d/%m/%Y %H:%M'),
                'Aktif' if trainer.is_active else 'Pasif'
            ],
            'is_active': trainer.is_active
        })
    
    context = {
        'trainers': trainer_data,
        'title': 'Eğitmenler'
    }
    return render(request, 'regame/trainer/list.html', context)

@login_required
def update_trainer(request, pk):
    trainer = get_object_or_404(User, pk=pk, is_staff=True)
    
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        
        # Bilgileri güncelle
        trainer.first_name = first_name
        trainer.last_name = last_name
        trainer.email = email
        trainer.save()
        
        messages.success(request, 'Eğitmen bilgileri başarıyla güncellendi.')
        return redirect('trainer_list')
    
    context = {
        'trainer': trainer,
        'title': 'Eğitmen Güncelle'
    }
    return render(request, 'regame/trainer/update.html', context)
