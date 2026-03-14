from django.contrib import admin

from accounts.models import User, Player, InvitedManager


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
   list_display = ('email', 'name', 'contact', 'role', 'is_superuser')
   list_display_links = ('email', 'name', 'contact', 'role')
   search_fields = ('email', 'name')
   ordering = ('name',)

   exclude = ('password', 'user_permissions', 'groups', 'otp', 'otp_expiry')
   readonly_fields = ('email', 'name', 'photo', 'date_of_birth', 'role', 'contact', 'favorite_player', 'favorite_team', 'last_login')



@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
   list_display = ('user', 'rating', 'games_played', 'goals', 'assists')
   list_display_links = ('user', 'rating', 'games_played', 'goals', 'assists')
   exclude = ('slug',)
   search_fields = ('user__name', 'user__email')

   readonly_fields = ('rating', 'games_played')
   ordering = ('-goals', '-assists', '-rating', 'user')


@admin.register(InvitedManager)
class InvitedManagerAdmin(admin.ModelAdmin):
   list_display = ('email', 'created_at')
   list_display_links = ('email', 'created_at')
   readonly_fields = ('email', 'created_at', 'expiry')
