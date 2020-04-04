import random

from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.utils.functional import cached_property
from model_utils import Choices
from model_utils.models import TimeStampedModel

from questions.models import QuestionGroup, Question, Answer


class GameQuerySet(models.QuerySet):
    def awaiting(self):
        return self.annotate(
            players_count=models.Count('players')
        ).filter(is_active=True, players_count=1)


class Game(TimeStampedModel):
    objects = GameQuerySet.as_manager()

    topic = models.ForeignKey(
        QuestionGroup,
        related_name="games",
        on_delete=models.DO_NOTHING,
    )
    password = models.CharField(max_length=8, blank=True)
    initial_hp = models.PositiveSmallIntegerField(default=100)
    questions_limit = models.PositiveSmallIntegerField(default=100)
    is_active = models.BooleanField(default=True)
    questions_ids = ArrayField(
        base_field=models.PositiveIntegerField,
        blank=True,
        null=True,
    )

    class Meta:
        ordering = ['-created']

    def __str__(self):
        return f"ID {self.pk}: {self.topic}"

    def save(self, *args, **kwargs):
        if not self.questions_ids:
            self.questions_ids = self.generate_questions_ids()
        super().save(*args, **kwargs)

    @cached_property
    def host(self):
        host = self.players.filter(role="host").first()
        return host or None

    @cached_property
    def guest(self):
        guest = self.players.filter(role="guest").first()
        return guest or None

    def generate_questions_ids(self):
        questions_ids = Question.objects.filter(
            topic=self.topic,
        ).values_list('id', flat=True)
        random.shuffle(questions_ids)
        if len(questions_ids) > self.questions_limit:
            return questions_ids[:self.questions_limit]
        else:
            return questions_ids


class Player(models.Model):
    """
    Represents player in specific game
    """
    ROLE_CHOICES = Choices(
        ("host", "Host"),
        ("guest", "Guest"),
    )
    game = models.ForeignKey(
        Game,
        related_name="players",
        on_delete=models.CASCADE,
    )
    profile = models.ForeignKey(
        'users.Profile',
        related_name="players",
        on_delete=models.SET_NULL,
        null=True,
    )
    role = models.CharField(
        max_length=255,
        choices=ROLE_CHOICES,
    )
    hp = models.PositiveSmallIntegerField(default=100)
    bullets_amount = models.PositiveSmallIntegerField(default=0)
    bullets_limit = models.PositiveSmallIntegerField(default=6)  # TODO: add config
    right_answers_count = models.PositiveSmallIntegerField(default=0)
    current_question_number = models.PositiveSmallIntegerField(default=0)

    def __str__(self):
        return self.profile

    def get_current_question(self):
        return Question.objects.get(
            pk=self.game.questions_ids[self.current_question_number]
        )

    def perform_answer(self, answer_pk):
        if answer_pk == Answer.objects.filter(
            question=self.get_current_question(),
            is_right=True,
        ).first().pk:
            self.right_answers_count += 1
            if self.bullets_amount < self.bullets_limit:
                self.bullets_amount += 1
        else:
            self.right_answers_count = 0
            self.bullets_amount = 0
            # TODO: add singleton for global config
            self.hp -= 3
        self.current_question_number += 1
        self.save()

    def get_power(self):
        return self.bullets_amount * 2


class PlayerAnswer(models.Model):
    player = models.ForeignKey(
        Player,
        related_name="answers",
        on_delete=models.CASCADE,
    )
    question = models.ForeignKey(
        Question,
        related_name="player_answers",
        on_delete=models.CASCADE,
    )
    answer = models.ForeignKey(
        Answer,
        related_name="player_answers",
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return str(self.pk)


class GameStateUpdate(TimeStampedModel):
    game = models.ForeignKey(
        Game,
        related_name="state_updates",
        on_delete=models.CASCADE,
    )
    ...
