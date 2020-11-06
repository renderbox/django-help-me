from .models import Ticket


class TicketMetaMixin():
    """
    Mixin that grabs the user meta information from a support request
    """
    
    def get_ticket_request_meta(self, request):
        user_agent = request.user_agent
        
        if user_agent.is_mobile:
            device = "mobile"
        elif user_agent.is_pc:
            device = "pc"
        elif user_agent.is_tablet:
            device = "tablet"
        else:
            device = "unknown"

        user_meta = {
            "browser": {
                "family": str.lower(user_agent.browser.family),
                "version": user_agent.browser.version_string
            },
            "os": {
                "family": str.lower(user_agent.os.family),
                "version": user_agent.os.version_string
            },
            "device": str.lower(user_agent.device.family),
            "mobile_tablet_or_pc": device,
            "ip_address": request.META['REMOTE_ADDR']
        }

        return user_meta
