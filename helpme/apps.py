from django.apps import AppConfig


class HelpMeConfig(AppConfig):
    name = 'helpme'
    configs = ["helpme.config.SupportEmailClass"]
