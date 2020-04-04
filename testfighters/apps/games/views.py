from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.views.generic import ListView, CreateView
from django.views.generic import View

from config import settings
from games.forms import NewGameForm
from games.models import Game, Player


class WaitingGamesListView(ListView):
    model = Game
    paginate_by = 20
    template_name = "fights/games_list.html"
    allow_empty = True
    queryset = Game.objects.awaiting()


class WelcomeView(View):

    def get(self, request, *args, **kwargs):
        context = {'game_id': None, 'games': Game.objects.awaiting().count()}
        if request.user.is_authenticated:
            profile = request.user.profile
            # TODO: HERE IS KOSTYL IN VIEW! REMOVE IT
            if profile.games_host.filter(is_active=True).count() > 0:
                context['game_id'] = profile.games_host.filter(is_active=True)[0].pk
            elif profile.games_guest.filter(is_active=True).count() > 0:
                context['game_id'] = profile.games_guest.filter(is_active=True)[0].pk
        return render(request, 'fights/index.html', context)


class ClientView(View):
    def get(self, request, *args, **kwargs):
        game_id = kwargs['game_id']
        game = Game.objects.get(pk=game_id)
        if game.host.profile.user == request.user:
            role = 'host'
            is_dead = game.host.hp <= 0
        else:
            role = 'guest'
            is_dead = game.guest.hp <= 0

        context = {
            'game_id': game_id,
            'role': role,
            'active': game.is_active,
            'is_dead': is_dead,
            # 'socket_url': settings.SOCKET_URL
        }
        return render(request, 'fights/client.html', context)


class NewGameView(CreateView):
    form_class = NewGameForm
    template_name = 'fights/new_game.html'

    def get_success_url(self):
        return reverse('games:client', args=[self.object.pk])

    def form_valid(self, form):
        ret = super().form_valid(form)
        Player.objects.create(
            game=self.object,
            profile=self.request.user.profile,
            hp=self.object.initial_hp,
            role=Player.ROLE_CHOICES.host,
        )
        return ret
