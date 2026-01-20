from .models import SystemSettings

def global_settings(request):
    # Get the settings object, or create it if it doesn't exist
    settings_obj, created = SystemSettings.objects.get_or_create(id=1)
    # Return the WHOLE object so we can access system_settings.theme AND system_settings.currency_symbol
    return {'system_settings': settings_obj}
