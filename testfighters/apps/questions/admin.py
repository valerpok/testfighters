from django.contrib import admin

from questions.models import QuestionGroup, Question, Answer


@admin.register(QuestionGroup)
class QuestionGroupAdmin(admin.ModelAdmin):
    ...


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    ...


@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    ...
