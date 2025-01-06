from django.db import models
from django.contrib.auth.models import User
from django.core.serializers.json import DjangoJSONEncoder
import json

class Company(models.Model):
    name = models.CharField(max_length=255, verbose_name="Adı")
    logo = models.ImageField(upload_to="company_logos/", blank=True, null=True, verbose_name="Logo")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Oluşturulma Tarihi")
    last_updated_at = models.DateTimeField(auto_now=True, verbose_name="Son Güncellenme Tarihi")
    is_active = models.BooleanField(default=True, verbose_name="Aktif Mi?")

    def __str__(self):
        return self.name

class Presentation(models.Model):
    company = models.ForeignKey('Company', on_delete=models.CASCADE, related_name="presentations", verbose_name="Şirket")
    name = models.CharField(max_length=255, verbose_name="Adı")
    bg_image = models.ImageField(upload_to="presentation_bg/", blank=True, null=True, verbose_name="Arka Plan Görseli")
    questions = models.JSONField(verbose_name="Sorular", encoder=DjangoJSONEncoder, decoder=json.JSONDecoder, blank=True,null=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Oluşturulma Tarihi")
    last_updated_at = models.DateTimeField(auto_now=True, verbose_name="Son Güncellenme Tarihi")
    is_active = models.BooleanField(default=True, verbose_name="Aktif Mi?")

    def __str__(self):
        return self.name


class Participant(models.Model):
    name = models.CharField(max_length=255, verbose_name="Adı")
    email = models.EmailField(unique=True, verbose_name="E-posta")
    company = models.ForeignKey(Company, on_delete=models.SET_NULL, null=True, blank=True, related_name="participants", verbose_name="Şirket")
    office = models.CharField(max_length=255, blank=True, null=True, verbose_name="Ofis")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Oluşturulma Tarihi")
    last_updated_at = models.DateTimeField(auto_now=True, verbose_name="Son Güncellenme Tarihi")
    is_active = models.BooleanField(default=True, verbose_name="Aktif Mi?")

    def __str__(self):
        return self.name

class Classroom(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="classrooms", verbose_name="Şirket")
    presentation = models.ForeignKey(Presentation, on_delete=models.CASCADE, related_name="classrooms", verbose_name="Sunum", blank=True, null=True)
    participants = models.ManyToManyField(Participant, verbose_name=("Katılımcılar"), blank=True, null=True)
    code = models.CharField(max_length=50, unique=True, verbose_name="Kod")
    qr_image = models.ImageField(upload_to="qr_codes/", blank=True, null=True, verbose_name="QR Kod")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Oluşturulma Tarihi")
    last_updated_at = models.DateTimeField(auto_now=True, verbose_name="Son Güncellenme Tarihi")
    is_active = models.BooleanField(default=True, verbose_name="Aktif Mi?")

    def __str__(self):
        return self.code

class Answer(models.Model):
    participant = models.ForeignKey(Participant, on_delete=models.CASCADE, related_name="answers", verbose_name="Katılımcı")
    presentation = models.ForeignKey(Presentation, on_delete=models.CASCADE, related_name="answers", verbose_name="Sunum")
    classroom = models.ForeignKey(Classroom, on_delete=models.CASCADE, related_name="answers", verbose_name="Classroom")
    answers = models.JSONField(verbose_name="Cevaplar", encoder=DjangoJSONEncoder, decoder=json.JSONDecoder)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Oluşturulma Tarihi")
    last_updated_at = models.DateTimeField(auto_now=True, verbose_name="Son Güncellenme Tarihi")
    is_active = models.BooleanField(default=True, verbose_name="Aktif Mi?")

    def __str__(self):
        return f"{self.participant.name} - {self.presentation}"