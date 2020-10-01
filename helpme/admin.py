from django.contrib import admin

from helpme.models import Ticket, Comment, Team, Question, Category

class TicketAdmin(admin.ModelAdmin):
    readonly_fields=('created', 'updated',)

admin.site.register(Ticket, TicketAdmin)
admin.site.register(Comment)
admin.site.register(Team)
admin.site.register(Category)
admin.site.register(Question)
