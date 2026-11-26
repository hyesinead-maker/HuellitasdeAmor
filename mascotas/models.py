
from django.db import models
from django.db.models import Q
from django.contrib.auth.models import User


# ==========================================
# MODELO DE MASCOTAS
# ==========================================

class Mascota(models.Model):

    ESPECIES = [
        ('Perro', 'Perro'),
        ('Gato', 'Gato'),
        ('Otro', 'Otro'),
    ]

    nombre = models.CharField(
        max_length=100
    )

    especie = models.CharField(
        max_length=20,
        choices=ESPECIES
    )

    raza = models.CharField(
        max_length=100,
        blank=True
    )

    edad = models.PositiveIntegerField(
        help_text="Edad aproximada en meses"
    )

    descripcion = models.TextField()

    foto = models.ImageField(
        upload_to='mascotas/',
        blank=True,
        null=True
    )

    disponible = models.BooleanField(
        default=True
    )

    fecha_registro = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return self.nombre


# ==========================================
# MODELO DE SOLICITUDES DE ADOPCIÓN
# ==========================================

class SolicitudAdopcion(models.Model):

    ESTADOS = [
        ('Pendiente', 'Pendiente'),
        ('Aprobada', 'Aprobada'),
        ('Rechazada', 'Rechazada'),
    ]

    usuario = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    mascota = models.ForeignKey(
        Mascota,
        on_delete=models.CASCADE
    )

    estado = models.CharField(
        max_length=20,
        choices=ESTADOS,
        default='Pendiente'
    )

    mensaje = models.TextField(
        blank=True
    )

    fecha = models.DateTimeField(
        auto_now_add=True
    )

    # ======================================
    # RESTRICCIONES DE SEGURIDAD
    # ======================================

    class Meta:

        constraints = [

            # Un usuario solo puede solicitar
            # una vez a la misma mascota.

            models.UniqueConstraint(
                fields=['usuario', 'mascota'],
                name='solicitud_unica_usuario_mascota'
            ),

            # Una mascota solamente puede tener
            # una solicitud aprobada.

            models.UniqueConstraint(
                fields=['mascota'],
                condition=Q(estado='Aprobada'),
                name='una_aprobacion_por_mascota'
            ),

        ]

    def __str__(self):
        return (
            f"{self.usuario.username} - "
            f"{self.mascota.nombre}"
        )


# ==========================================
# MODELO DE RESEÑAS
# ==========================================

class Resena(models.Model):

    CALIFICACIONES = [
        (1, '1 estrella'),
        (2, '2 estrellas'),
        (3, '3 estrellas'),
        (4, '4 estrellas'),
        (5, '5 estrellas'),
    ]

    usuario = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    titulo = models.CharField(
        max_length=150
    )

    comentario = models.TextField()

    calificacion = models.IntegerField(
        choices=CALIFICACIONES,
        default=5
    )

    fecha = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return (
            f"{self.titulo} - "
            f"{self.usuario.username}"
        )


# ==========================================
# MODELO DE MENSAJES DEL CHAT
# ==========================================

class MensajeChat(models.Model):

    # Usuario al que pertenece la conversación.
    # Los administradores responderán dentro
    # de la conversación de este usuario.

    usuario = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='mensajes_chat'
    )

    # Identifica quién envió el mensaje.

    REMITENTES = [
        ('usuario', 'Usuario'),
        ('administrador', 'Administrador'),
    ]

    remitente = models.CharField(
        max_length=20,
        choices=REMITENTES
    )

    # Contenido del mensaje.

    contenido = models.TextField(
        max_length=2000
    )

    # Fecha y hora de envío.

    fecha = models.DateTimeField(
        auto_now_add=True
    )

    # Indica si el destinatario ya lo leyó.

    leido = models.BooleanField(
        default=False
    )

    # ======================================
    # CONFIGURACIÓN DEL MODELO
    # ======================================

    class Meta:

        ordering = ['fecha', 'id']

        verbose_name = 'Mensaje de chat'
        verbose_name_plural = 'Mensajes de chat'

    def __str__(self):

        return (
            f"{self.get_remitente_display()} - "
            f"{self.usuario.username} - "
            f"{self.fecha:%d/%m/%Y %H:%M}"
        )
