# from rest_framework import viewsets
#
#
# class GameViewSet(viewsets.ModelViewSet):
#     permission_classes = [IsHostOrGuest, GameIsActive]
#     queryset = Game.objects.all().order_by('id')
#     serializer_class = GameSerializer
#
#     def get_queryset(self):
#         if self.action == 'list':
#             print('eheheh')
#             return Game.objects.filter(is_active=True, guest=None).order_by('-pk')
#         return self.queryset
#
#     def get_serializer_class(self):
#
#         if self.action == 'list':
#             return ListGameSerializer
#         elif self.action == 'create':
#             return NewGameSerializer
#         elif self.action == 'answer':
#             return AnswerGameSerializer
#         elif self.action == 'join':
#             return JoinGameSerializer
#         else:
#             return self.serializer_class
#
#     @detail_route(methods=['patch'])
#     def join(self, request, pk=None):
#         game = self.get_object()
#
#         player = Player.get_player_or_create(request.user)
#
#         if player.has_active_games():
#             return HttpResponse(status=status.HTTP_403_FORBIDDEN)
#
#         # If game already have guest
#         if game.guest:
#             return HttpResponse(status=status.HTTP_403_FORBIDDEN)
#
#         password = request.data.get('password', None)
#         # Check, if game has password and this password isn't equal to entered password
#         if game.password and game.password != password:
#                 return HttpResponse(status=status.HTTP_403_FORBIDDEN)
#
#         game.join(request.user)
#         return HttpResponse(status=status.HTTP_202_ACCEPTED)
#
#     @detail_route(methods=['patch'])
#     def attack(self, request, pk=None):
#         game = self.get_object()
#         game.attack(request.user)
#         return HttpResponse(status=status.HTTP_202_ACCEPTED)
#
#     @detail_route(methods=['patch'])
#     def answer(self, request, pk=None):
#         game = self.get_object()
#         game.answer(request.user, request.data.get('answer_id', None))
#         return HttpResponse(status=status.HTTP_202_ACCEPTED)
#
#     @detail_route(methods=['patch'])
#     def surrender(self, request, pk=None):
#         game = self.get_object()
#         game.leave_game(request.user)
#         return HttpResponse(status=status.HTTP_202_ACCEPTED)
