
from django.contrib import admin
from django.db import transaction

from .models import Mascota, SolicitudAdopcion, Resena
from .forms import SolicitudAdopcionAdminForm


# ==========================================
# ADMINISTRACIÓN DE MASCOTAS
# ==========================================

@admin.register(Mascota)
class MascotaAdmin(admin.ModelAdmin):

    list_display = (
        'nombre',
        'especie',
        'raza',
        'edad',
        'disponible',
        'fecha_registro'
    )

    list_filter = (
        'especie',
        'disponible'
    )

    search_fields = (
        'nombre',
        'raza'
    )


# ==========================================
# ADMINISTRACIÓN DE SOLICITUDES
# ==========================================

@admin.register(SolicitudAdopcion)
class SolicitudAdopcionAdmin(admin.ModelAdmin):

    # Formulario de validación
    form = SolicitudAdopcionAdminForm

    # Columnas del administrador
    list_display = (
        'usuario',
        'mascota',
        'estado',
        'tiene_motivo',
        'fecha'
    )

    # Filtros
    list_filter = (
        'estado',
        'fecha'
    )

    # Buscador
    search_fields = (
        'usuario__username',
        'mascota__nombre',
        'mensaje'
    )

    # Campos que no pueden modificarse
    readonly_fields = (
        'usuario',
        'mascota',
        'mensaje',
        'fecha'
    )

    # Organización del formulario
    fieldsets = (
        (
            'Información del solicitante',
            {
                'fields': (
                    'usuario',
                    'mascota',
                    'fecha'
                )
            }
        ),
        (
            'Motivo de adopción',
            {
                'fields': (
                    'mensaje',
                ),
                'description': (
                    'Este es el motivo que escribió '
                    'el usuario al solicitar la adopción.'
                )
            }
        ),
        (
            'Administración de la solicitud',
            {
                'fields': (
                    'estado',
                ),
                'description': (
                    'Puedes aprobar o rechazar '
                    'la solicitud de adopción.'
                )
            }
        )
    )

    # Mostrar si la solicitud tiene motivo
    @admin.display(
        boolean=True,
        description='Motivo registrado'
    )
    def tiene_motivo(self, obj):
        return bool(obj.mensaje and obj.mensaje.strip())

    # No permitir crear solicitudes desde el admin
    def has_add_permission(self, request):
        return False

    # Desactivar acciones masivas
    actions = None

    # ==========================================
    # GUARDAR SOLICITUD DE ADOPCIÓN
    # ==========================================

    def save_model(self, request, obj, form, change):

        with transaction.atomic():

            # Guardar la solicitud
            obj.save()

            # Si la solicitud fue aprobada
            if obj.estado == 'Aprobada':

                # Marcar la mascota como no disponible
                Mascota.objects.filter(
                    pk=obj.mascota_id
                ).update(
                    disponible=False
                )

                # Rechazar automáticamente las demás
                # solicitudes pendientes de esa mascota
                SolicitudAdopcion.objects.filter(
                    mascota_id=obj.mascota_id,
                    estado='Pendiente'
                ).exclude(
                    pk=obj.pk
                ).update(
                    estado='Rechazada'
                )


# ==========================================
# ADMINISTRACIÓN DE RESEÑAS
# ==========================================

@admin.register(Resena)
class ResenaAdmin(admin.ModelAdmin):

    list_display = (
        'titulo',
        'usuario',
        'calificacion',
        'fecha'
    )

    list_filter = (
        'calificacion',
        'fecha'
    )

    search_fields = (
        'titulo',
        'usuario__username'
    )

    readonly_fields = (
        'usuario',
        'fecha'
    )

    # Los administradores no pueden crear reseñas
    def has_add_permission(self, request):
        return False




