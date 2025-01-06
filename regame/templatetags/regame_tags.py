from django import template

register = template.Library()

@register.filter
def dictget(questions_list, question_number):
    """Soru numarasına göre soruyu bulur"""
    for question in questions_list:
        if question['question_number'] == question_number:
            return question
    return None 