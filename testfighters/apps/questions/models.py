from django.db import models
from model_utils.models import SoftDeletableModel


class QuestionGroup(SoftDeletableModel):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Question(models.Model):
    text = models.TextField(max_length=1000)
    topic = models.ForeignKey(
        QuestionGroup,
        related_name="questions",
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return f'{self.topic}: {self.preview}'

    @property
    def preview(self):
        if len(self.text) < 100:
            return self.text
        return self.text[:100]


class Answer(models.Model):
    text = models.TextField(max_length=1000)
    is_right = models.BooleanField(default=False)
    question = models.ForeignKey(
        Question,
        related_name="answers",
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return self.preview

    @property
    def preview(self):
        if len(self.text) < 100:
            return self.text
        return self.text[:100]
