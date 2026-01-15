from .models import SystemSettings

def global_settings(request):
    # Get the settings object, or create it if it doesn't exist
    settings_obj, created = SystemSettings.objects.get_or_create(id=1)
    return {
        'currency': settings_obj.currency_symbol
    }
