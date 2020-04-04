from rest_framework import serializers

from games.models import Game


class GameSerializer(serializers.ModelSerializer):
    question_text = serializers.SerializerMethodField()
    choices = serializers.SerializerMethodField()
    host = serializers.CharField(source='host')
    guest = serializers.SerializerMethodField()
    topic = serializers.CharField(source='topic.name')

    class Meta:
        model = Game
        fields = (
            'id',
            'topic',
            'host',
            'guest',
            'question_text',
            'choices'
        )

    def get_guest(self, obj):
        if obj.guest:
            return obj.guest.name
        return 'Nobody joined yet'

    def get_question(self, obj):
        """
        Get current question for host or guest.
        """
        player = Player.objects.get(user=self.context['request'].user)
        question = obj.get_question(player)

        return question

    def get_question_text(self, obj):
        """
        Get text for representation in serializer
        """
        question = self.get_question(obj)
        question_text = question.text
        return question_text

    def get_choices(self, obj):
        question = self.get_question(obj)
        choices = question.related_choices.all()
        choices_text = [{'choice_id': choice.id, 'choice_text': choice.text} for choice in choices]
        return choices_text


class NewGameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Game
        fields = (
            'id',
            'topic',
            'password',
        )

    def save(self, **kwargs):
        user = self.context['request'].user
        player = Player.get_player_or_create(user)

        kwargs['host'] = player
        super().save(**kwargs)


class ListGameSerializer(serializers.ModelSerializer):
    host = serializers.CharField(source='host.name')
    topic = serializers.CharField(source='topic.name')
    password = serializers.SerializerMethodField()

    class Meta:
        model = Game
        fields = (
            'id',
            'topic',
            'host',
            'password',
        )

    def get_password(self, obj):
        if obj.password:
            return True
        return False


class AnswerGameSerializer(serializers.ModelSerializer):
    answer_id = serializers.IntegerField()

    class Meta:
        model = Game
        fields = (
            'id',
            'answer_id'
        )


class JoinGameSerializer(serializers.ModelSerializer):
    password = serializers.CharField()

    class Meta:
        model = Game
        fields = (
            'id',
            'password'
        )
