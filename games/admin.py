from django.contrib import admin

from games.models import (
   Game,
   Futsal,
   Goal,
   PlayerReviewRating,
   PlayerGameRating,
)


class AvailablePlayersInline(admin.TabularInline):
   model = Game.available_players.through
   extra = 0
   can_delete = False
   readonly_fields = ('player',)
   
   verbose_name = "Available Player"


class TeamAPlayersInline(admin.TabularInline):
   model = Game.teamA.through
   extra = 0
   
   verbose_name = "Team A Player"
   verbose_name_plural = "Team A Players"


class TeamBPlayersInline(admin.TabularInline):
   model = Game.teamB.through
   extra = 0

   verbose_name = "Team B Player"
   verbose_name_plural = "Team B Players"


@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
   list_display = ('game_id', 'goalsA', 'goalsB', 'date', 'time', 'futsal', 'is_complete')
   list_display_links = ('game_id', 'date', 'time', 'futsal')
   readonly_fields = ('game_id',)

   fieldsets = (
      ('Game Details', {
         "fields": ('game_id', 'date', 'time', 'futsal', 'is_complete')
      }),
      ('Game Stats', {
         "fields": ('goalsA', 'goalsB')
      })
   )

   inlines = (AvailablePlayersInline, TeamAPlayersInline, TeamBPlayersInline)



@admin.register(Futsal)
class FutsalAdmin(admin.ModelAdmin):
   list_display = ('name', 'location')
   list_display_links = ('name', 'location')


@admin.register(PlayerReviewRating)
class PlayerReviewRatingAdmin(admin.ModelAdmin):
   list_display = ('player', 'game', 'rating_player', 'rating')
   list_display_links = ('player', 'game', 'rating_player', 'rating')
   readonly_fields = ('player', 'game', 'rating_player', 'rating')


@admin.register(PlayerGameRating)
class PlayerGameRatingAdmin(admin.ModelAdmin):
   list_display = ('player', 'game', 'rating')
   list_display_links = ('player', 'game', 'rating')
   # readonly_fields  = ('player', 'game', 'rating')


admin.site.register(Goal)