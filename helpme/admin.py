from django.contrib import admin

from helpme.models import Ticket

class TicketAdmin(admin.ModelAdmin):
    readonly_fields=('created', 'updated',)

admin.site.register(Ticket, TicketAdmin)
