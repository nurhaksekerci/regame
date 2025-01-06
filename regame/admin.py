from django.contrib import admin
from .models import Company, Presentation, Classroom, Participant, Answer

@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at', 'last_updated_at', 'is_active')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name',)
    readonly_fields = ('created_at', 'last_updated_at')
    ordering = ('-created_at',)
    list_per_page = 20

@admin.register(Presentation)
class PresentationAdmin(admin.ModelAdmin):
    list_display = ('name', 'company', 'created_at', 'last_updated_at', 'is_active')
    list_filter = ('company', 'is_active', 'created_at')
    search_fields = ('name', 'company__name')
    readonly_fields = ('created_at', 'last_updated_at')
    ordering = ('-created_at',)
    list_per_page = 20

@admin.register(Classroom)
class ClassroomAdmin(admin.ModelAdmin):
    list_display = ('code', 'company', 'presentation', 'created_at', 'last_updated_at', 'is_active')
    list_filter = ('company', 'presentation', 'is_active', 'created_at')
    search_fields = ('code', 'company__name', 'presentation__name')
    readonly_fields = ('created_at', 'last_updated_at', 'code')
    ordering = ('-created_at',)
    list_per_page = 20

    def get_readonly_fields(self, request, obj=None):
        # Eğer bu yeni bir kayıtsa (obj=None), code alanı readonly olmasın
        if obj is None:
            return ('created_at', 'last_updated_at')
        # Mevcut kayıt için code alanı readonly olsun
        return ('created_at', 'last_updated_at', 'code')

@admin.register(Participant)
class ParticipantAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'company', 'office', 'created_at', 'is_active')
    list_filter = ('company', 'is_active', 'created_at')
    search_fields = ('name', 'email', 'office', 'company__name')
    readonly_fields = ('created_at', 'last_updated_at')
    ordering = ('-created_at',)
    list_per_page = 20

@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ('participant', 'presentation', 'classroom', 'created_at', 'is_active', 'get_answers_display')
    list_filter = ('presentation', 'classroom', 'is_active', 'created_at')
    search_fields = ('participant__name', 'presentation__name', 'classroom__code')
    readonly_fields = ('created_at', 'last_updated_at')
    ordering = ('-created_at',)
    list_per_page = 20

    def get_answers_display(self, obj):
        """JSON formatındaki cevapları daha okunabilir göster"""
        if obj.answers:
            return "\n".join([
                f"Soru {a['question_number']}: {a['question_text']}\n"
                f"Cevap: {a['answer_text']}"
                for a in obj.answers
            ])
        return "-"
    get_answers_display.short_description = "Cevaplar"

    def get_readonly_fields(self, request, obj=None):
        # Varsayılan readonly alanlar
        readonly_fields = ['created_at', 'last_updated_at']
        # Eğer bu mevcut bir kayıtsa, answers alanını da readonly yap
        if obj:
            readonly_fields.append('answers')
        return readonly_fields
