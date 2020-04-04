from django import forms

from games.models import Game, Player


class NewGameForm(forms.ModelForm):
    class Meta:
        model = Game
        fields = (
            'topic',
            'password',
            'initial_hp',
            'questions_limit',
        )
