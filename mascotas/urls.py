
from django.urls import path
from . import views


urlpatterns = [

    # ==========================================
    # PÁGINAS PRINCIPALES
    # ==========================================

    path(
        '',
        views.inicio,
        name='inicio'
    ),

    path(
        'catalogo/',
        views.catalogo,
        name='catalogo'
    ),

    # ==========================================
    # PÁGINA DE ADOPCIONES
    # ==========================================

    path(
        'adopciones/',
        views.adopciones,
        name='adopciones'
    ),

    path(
        'mascota/<int:mascota_id>/',
        views.detalle_mascota,
        name='detalle_mascota'
    ),

    # ==========================================
    # PÁGINA NOSOTROS
    # ==========================================

    path(
        'nosotros/',
        views.nosotros,
        name='nosotros'
    ),

    # ==========================================
    # USUARIOS
    # ==========================================

    path(
        'registro/',
        views.registro,
        name='registro'
    ),

    path(
        'login/',
        views.iniciar_sesion,
        name='login'
    ),

    path(
        'logout/',
        views.cerrar_sesion,
        name='logout'
    ),

    path(
        'perfil/',
        views.perfil,
        name='perfil'
    ),

    # ==========================================
    # EDITAR PERFIL DEL USUARIO
    # ==========================================

    path(
        'perfil/editar/',
        views.editar_perfil,
        name='editar_perfil'
    ),

    # ==========================================
    # CAMBIAR CONTRASEÑA
    # ==========================================

    path(
        'perfil/cambiar-contrasena/',
        views.cambiar_contrasena,
        name='cambiar_contrasena'
    ),

    # ==========================================
    # SOLICITUDES DE ADOPCIÓN
    # ==========================================

    path(
        'mascota/<int:mascota_id>/solicitar/',
        views.solicitar_adopcion,
        name='solicitar_adopcion'
    ),

    # ==========================================
    # RESEÑAS
    # ==========================================

    path(
        'resenas/',
        views.ver_resenas,
        name='ver_resenas'
    ),

    path(
        'resenas/crear/',
        views.crear_resena,
        name='crear_resena'
    ),

    path(
        'resenas/eliminar/<int:resena_id>/',
        views.eliminar_resena,
        name='eliminar_resena'
    ),

    path(
        'resenas/editar/<int:resena_id>/',
        views.editar_resena,
        name='editar_resena'
    ),

    # ==========================================
    # CHAT DEL USUARIO
    # ==========================================

    path(
        'chat/',
        views.chat_usuario,
        name='chat_usuario'
    ),

    # ==========================================
    # PANEL ADMINISTRATIVO
    # ==========================================

    path(
        'administracion/',
        views.panel_administrador,
        name='panel_administrador'
    ),

    # ==========================================
    # ADMINISTRACIÓN DE RESEÑAS
    # ==========================================

    path(
        'administracion/resenas/',
        views.gestionar_resenas,
        name='gestionar_resenas'
    ),

    # ==========================================
    # ADMINISTRACIÓN DE USUARIOS
    # ==========================================

    path(
        'administracion/usuarios/',
        views.gestionar_usuarios,
        name='gestionar_usuarios'
    ),

    # ==========================================
    # ADMINISTRACIÓN DE MASCOTAS
    # ==========================================

    path(
        'administracion/mascotas/agregar/',
        views.agregar_mascota,
        name='agregar_mascota'
    ),

    path(
        'administracion/mascotas/',
        views.gestionar_mascotas,
        name='gestionar_mascotas'
    ),

    path(
        'administracion/mascotas/editar/<int:mascota_id>/',
        views.editar_mascota,
        name='editar_mascota'
    ),

    path(
        'administracion/mascotas/eliminar/<int:mascota_id>/',
        views.eliminar_mascota,
        name='eliminar_mascota'
    ),

    # ==========================================
    # ADMINISTRACIÓN DE SOLICITUDES
    # ==========================================

    path(
        'administracion/solicitudes/',
        views.gestionar_solicitudes,
        name='gestionar_solicitudes'
    ),

    path(
        'administracion/solicitudes/aprobar/<int:solicitud_id>/',
        views.aprobar_solicitud,
        name='aprobar_solicitud'
    ),

    path(
        'administracion/solicitudes/rechazar/<int:solicitud_id>/',
        views.rechazar_solicitud,
        name='rechazar_solicitud'
    ),

    # ==========================================
    # NUEVO: BANDEJA DE MENSAJES
    # DEL ADMINISTRADOR
    # ==========================================

    path(
        'administracion/mensajes/',
        views.bandeja_mensajes,
        name='bandeja_mensajes'
    ),

    # ==========================================
    # NUEVO: RESPONDER A UN USUARIO
    # ==========================================

    path(
        'administracion/mensajes/usuario/<int:usuario_id>/',
        views.chat_administrador,
        name='chat_administrador'
    ),

]


