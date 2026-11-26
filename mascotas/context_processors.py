
from .models import MensajeChat


def notificaciones_chat(request):

    notificaciones = 0

    if request.user.is_authenticated:

        if request.user.is_superuser:

            notificaciones = MensajeChat.objects.filter(
                remitente='usuario',
                leido=False
            ).count()

        elif not request.user.is_staff:

            notificaciones = MensajeChat.objects.filter(
                usuario=request.user,
                remitente='administrador',
                leido=False
            ).count()

    return {
        'notificaciones_chat': notificaciones
    }
