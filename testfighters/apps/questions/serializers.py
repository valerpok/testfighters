from rest_framework import serializers

from questions.models import QuestionGroup, Question, Answer


class AnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer
        fields = (
            'id',
            'text',
        )


class QuestionSerializer(serializers.ModelSerializer):
    answers = AnswerSerializer(many=True)

    class Meta:
        model = Question
        fields = (
            'id',
            'text',
            'answers',
        )
