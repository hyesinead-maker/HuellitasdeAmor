
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db import transaction, IntegrityError
from django.core.exceptions import PermissionDenied
from .models import Mascota, Resena, SolicitudAdopcion, MensajeChat
from .forms import RegistroUsuarioForm, ResenaForm, MascotaForm
from django.db.models import Count
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash



# ==========================================
# PÁGINA DE INICIO
# ==========================================

def inicio(request):

    mascotas = Mascota.objects.filter(
        disponible=True
    ).order_by('-fecha_registro')[:6]

    resenas = Resena.objects.select_related(
        'usuario'
    ).order_by('-fecha')[:6]

    contexto = {
        'mascotas': mascotas,
        'resenas': resenas,
    }

    return render(
        request,
        'mascotas/inicio.html',
        contexto
    )



# ==========================================
# PÁGINA PÚBLICA DE ADOPCIONES
# ==========================================

def adopciones(request):

    # Mostrar algunas mascotas disponibles.
    mascotas = Mascota.objects.filter(
        disponible=True
    ).order_by('-fecha_registro')[:3]

    # Mostrar las solicitudes del usuario
    # únicamente si inició sesión y no es administrador.
    solicitudes = []

    if (
        request.user.is_authenticated
        and not request.user.is_staff
        and not request.user.is_superuser
    ):

        solicitudes = SolicitudAdopcion.objects.filter(
            usuario=request.user
        ).select_related(
            'mascota'
        ).order_by('-fecha')[:3]

    contexto = {
        'mascotas': mascotas,
        'solicitudes': solicitudes,
    }

    return render(
        request,
        'mascotas/adopciones.html',
        contexto
    )



# ==========================================
# CATÁLOGO DE MASCOTAS
# ==========================================

def catalogo(request):

    mascotas = Mascota.objects.filter(
        disponible=True
    ).order_by('-fecha_registro')

    return render(
        request,
        'mascotas/catalogo.html',
        {
            'mascotas': mascotas
        }
    )


# ==========================================
# DETALLE DE MASCOTA
# ==========================================

def detalle_mascota(request, mascota_id):

    # Los superusuarios pueden ver todas las mascotas.
    if request.user.is_authenticated and request.user.is_superuser:

        mascota = get_object_or_404(
            Mascota,
            id=mascota_id
        )

    else:

        # Los usuarios normales y visitantes
        # solo pueden ver mascotas disponibles.
        mascota = get_object_or_404(
            Mascota,
            id=mascota_id,
            disponible=True
        )

    return render(
        request,
        'mascotas/detalle_mascota.html',
        {
            'mascota': mascota
        }
    )


# ==========================================
# REGISTRO DE USUARIOS
# ==========================================

def registro(request):

    if request.user.is_authenticated:
        return redirect('inicio')

    if request.method == 'POST':

        formulario = RegistroUsuarioForm(request.POST)

        if formulario.is_valid():

            usuario = formulario.save()

            login(request, usuario)

            messages.success(
                request,
                '¡Tu cuenta fue creada exitosamente!'
            )

            return redirect('inicio')

    else:
        formulario = RegistroUsuarioForm()

    return render(
        request,
        'mascotas/registro.html',
        {
            'formulario': formulario
        }
    )


# ==========================================
# INICIAR SESIÓN
# ==========================================

def iniciar_sesion(request):

    if request.user.is_authenticated:
        return redirect('inicio')

    if request.method == 'POST':

        username = request.POST.get(
            'username', ''
        ).strip()

        password = request.POST.get(
            'password', ''
        )

        usuario = authenticate(
            request,
            username=username,
            password=password
        )

        if usuario is not None:

            login(request, usuario)

            messages.success(
                request,
                '¡Bienvenido nuevamente a HuellistasdeAmor!'
            )

            return redirect('inicio')

        messages.error(
            request,
            'El usuario o la contraseña son incorrectos.'
        )

    return render(
        request,
        'mascotas/login.html'
    )


# ==========================================
# CERRAR SESIÓN
# ==========================================

def cerrar_sesion(request):

    if request.method == 'POST':

        logout(request)

        messages.success(
            request,
            'Has cerrado sesión correctamente.'
        )

    return redirect('inicio')


# ==========================================
# PERFIL DEL USUARIO
# ==========================================

@login_required(login_url='login')
def perfil(request):

    if request.user.is_staff or request.user.is_superuser:
        return redirect('admin:index')

    solicitudes = SolicitudAdopcion.objects.filter(
        usuario=request.user
    ).select_related(
        'mascota'
    ).order_by('-fecha')

    resenas = Resena.objects.filter(
        usuario=request.user
    ).order_by('-fecha')

    contexto = {
        'solicitudes': solicitudes,
        'resenas': resenas,
    }

    return render(
        request,
        'mascotas/perfil.html',
        contexto
    )


# ==========================================
# SOLICITAR ADOPCIÓN
# ==========================================

@login_required(login_url='login')
def solicitar_adopcion(request, mascota_id):

    # Impedir solicitudes de administradores.
    if request.user.is_staff or request.user.is_superuser:

        messages.error(
            request,
            'Los administradores no pueden solicitar adopciones.'
        )

        return redirect('catalogo')

    # Solo aceptar solicitudes POST.
    if request.method != 'POST':

        return redirect(
            'detalle_mascota',
            mascota_id=mascota_id
        )

    # Obtener el motivo de adopción.
    mensaje_adopcion = request.POST.get(
        'mensaje', ''
    ).strip()

    # Validar que no esté vacío.
    if not mensaje_adopcion:

        messages.error(
            request,
            'Debes escribir por qué deseas adoptar '
            'a esta mascota.'
        )

        return redirect(
            'detalle_mascota',
            mascota_id=mascota_id
        )

    # Validar mínimo de 20 caracteres.
    if len(mensaje_adopcion) < 20:

        messages.error(
            request,
            'El motivo de adopción debe contener '
            'al menos 20 caracteres.'
        )

        return redirect(
            'detalle_mascota',
            mascota_id=mascota_id
        )

    # Validar máximo de 1000 caracteres.
    if len(mensaje_adopcion) > 1000:

        messages.error(
            request,
            'El motivo de adopción no puede superar '
            'los 1000 caracteres.'
        )

        return redirect(
            'detalle_mascota',
            mascota_id=mascota_id
        )

    # Obtener mascota disponible.
    mascota = get_object_or_404(
        Mascota,
        id=mascota_id,
        disponible=True
    )

    # Comprobar solicitudes anteriores.
    if SolicitudAdopcion.objects.filter(
        usuario=request.user,
        mascota=mascota
    ).exists():

        messages.warning(
            request,
            'Ya has enviado una solicitud para esta mascota.'
        )

        return redirect('perfil')

    # Guardar solicitud.
    try:

        with transaction.atomic():

            # Comprobar disponibilidad nuevamente.
            if not Mascota.objects.filter(
                pk=mascota.pk,
                disponible=True
            ).exists():

                messages.error(
                    request,
                    'Esta mascota ya no está disponible.'
                )

                return redirect('catalogo')

            SolicitudAdopcion.objects.create(
                usuario=request.user,
                mascota=mascota,
                estado='Pendiente',
                mensaje=mensaje_adopcion
            )

    except IntegrityError:

        messages.warning(
            request,
            'No se pudo registrar la solicitud. '
            'Es posible que ya tengas una solicitud '
            'para esta mascota.'
        )

        return redirect('perfil')

    messages.success(
        request,
        f'¡Tu solicitud para adoptar a {mascota.nombre} '
        'se envió correctamente!'
    )

    return redirect('perfil')


# ==========================================
# CREAR RESEÑA
# ==========================================

@login_required(login_url='login')
def crear_resena(request):

    if request.user.is_staff or request.user.is_superuser:

        messages.error(
            request,
            'Los administradores no pueden publicar reseñas.'
        )

        return redirect('inicio')

    if request.method == 'POST':

        formulario = ResenaForm(request.POST)

        if formulario.is_valid():

            resena = formulario.save(commit=False)
            resena.usuario = request.user
            resena.save()

            messages.success(
                request,
                '¡Tu reseña fue publicada correctamente!'
            )

            return redirect('perfil')

    else:
        formulario = ResenaForm()

    return render(
        request,
        'mascotas/crear_resena.html',
        {
            'formulario': formulario
        }
    )



# ==========================================
# EDITAR RESEÑA
# ==========================================

@login_required(login_url='login')
def editar_resena(request, resena_id):

    resena = get_object_or_404(
        Resena,
        id=resena_id
    )

    es_administrador = (
        request.user.is_staff
        or request.user.is_superuser
    )

    es_propietario = (
        resena.usuario_id == request.user.id
    )

    if not es_administrador and not es_propietario:

        messages.error(
            request,
            'No tienes permiso para editar esta reseña.'
        )

        return redirect('perfil')

    if request.method == 'POST':

        formulario = ResenaForm(
            request.POST,
            instance=resena
        )

        if formulario.is_valid():

            formulario.save()

            messages.success(
                request,
                '¡La reseña fue actualizada correctamente!'
            )

            if es_administrador:

                return redirect(
                    'gestionar_resenas'
                )

            return redirect('perfil')

    else:

        formulario = ResenaForm(
            instance=resena
        )

    return render(
        request,
        'mascotas/editar_resena.html',
        {
            'formulario': formulario,
            'resena': resena
        }
    )




# ==========================================
# ELIMINAR RESEÑA
# ==========================================

@login_required(login_url='login')
def eliminar_resena(request, resena_id):

    resena = get_object_or_404(
        Resena,
        id=resena_id
    )

    es_administrador = (
        request.user.is_staff
        or request.user.is_superuser
    )

    es_propietario = (
        resena.usuario_id == request.user.id
    )

    if not es_administrador and not es_propietario:

        messages.error(
            request,
            'No tienes permiso para eliminar esta reseña.'
        )

        return redirect('perfil')

    # Solo eliminar mediante POST.
    if request.method == 'POST':

        resena.delete()

        messages.success(
            request,
            '¡La reseña fue eliminada correctamente!'
        )

        if es_administrador:

            return redirect(
                'gestionar_resenas'
            )

        return redirect('perfil')

    # Mostrar confirmación.
    return render(
        request,
        'mascotas/eliminar_resena.html',
        {
            'resena': resena
        }
    )


# ==========================================
# PANEL ADMINISTRATIVO - AGREGAR MASCOTA
# ==========================================

@login_required(login_url='login')
def agregar_mascota(request):

    # Solo los superusuarios pueden registrar mascotas.
    if not request.user.is_superuser:

        raise PermissionDenied(
            'No tienes permiso para agregar mascotas.'
        )

    if request.method == 'POST':

        formulario = MascotaForm(
            request.POST,
            request.FILES
        )

        if formulario.is_valid():

            mascota = formulario.save()

            messages.success(
                request,
                f'¡{mascota.nombre} fue registrada correctamente!'
            )

            return redirect('catalogo')

    else:
        formulario = MascotaForm()

    return render(
        request,
        'mascotas/admin_agregar_mascota.html',
        {
            'formulario': formulario
        }
    )


# ==========================================
# PANEL ADMINISTRATIVO PRINCIPAL
# ==========================================

@login_required(login_url='login')
def panel_administrador(request):

    # Permitir acceso únicamente a superusuarios.
    if not request.user.is_superuser:

        raise PermissionDenied(
            'No tienes permiso para acceder al panel.'
        )

    # Estadísticas generales.
    total_mascotas = Mascota.objects.count()

    mascotas_disponibles = Mascota.objects.filter(
        disponible=True
    ).count()

    total_usuarios = User.objects.filter(
        is_staff=False,
        is_superuser=False
    ).count()

    total_resenas = Resena.objects.count()

    solicitudes_pendientes = SolicitudAdopcion.objects.filter(
        estado='Pendiente'
    ).count()

    solicitudes_aprobadas = SolicitudAdopcion.objects.filter(
        estado='Aprobada'
    ).count()

    # Últimas mascotas registradas.
    ultimas_mascotas = Mascota.objects.order_by(
        '-fecha_registro'
    )[:5]

    # Solicitudes recientes.
    ultimas_solicitudes = SolicitudAdopcion.objects.select_related(
        'usuario',
        'mascota'
    ).order_by('-fecha')[:5]

    contexto = {
        'total_mascotas': total_mascotas,
        'mascotas_disponibles': mascotas_disponibles,
        'total_usuarios': total_usuarios,
        'total_resenas': total_resenas,
        'solicitudes_pendientes': solicitudes_pendientes,
        'solicitudes_aprobadas': solicitudes_aprobadas,
        'ultimas_mascotas': ultimas_mascotas,
        'ultimas_solicitudes': ultimas_solicitudes,
    }

    return render(
        request,
        'mascotas/panel_administrador.html',
        contexto
    )


# ==========================================
# PANEL ADMINISTRATIVO - GESTIONAR MASCOTAS
# ==========================================

@login_required(login_url='login')
def gestionar_mascotas(request):

    # Solo los superusuarios pueden administrar mascotas.
    if not request.user.is_superuser:

        raise PermissionDenied(
            'No tienes permiso para gestionar mascotas.'
        )

    # Obtener todas las mascotas registradas.
    mascotas = Mascota.objects.all().order_by(
        '-fecha_registro'
    )

    # Estadísticas de mascotas.
    total_mascotas = Mascota.objects.count()

    mascotas_disponibles = Mascota.objects.filter(
        disponible=True
    ).count()

    mascotas_no_disponibles = Mascota.objects.filter(
        disponible=False
    ).count()

    contexto = {
        'mascotas': mascotas,
        'total_mascotas': total_mascotas,
        'mascotas_disponibles': mascotas_disponibles,
        'mascotas_no_disponibles': mascotas_no_disponibles,
    }

    return render(
        request,
        'mascotas/gestionar_mascotas.html',
        contexto
    )


# ==========================================
# PANEL ADMINISTRATIVO - EDITAR MASCOTA
# ==========================================

@login_required(login_url='login')
def editar_mascota(request, mascota_id):

    # Solo los superusuarios pueden editar mascotas.
    if not request.user.is_superuser:

        raise PermissionDenied(
            'No tienes permiso para editar mascotas.'
        )

    # Buscar la mascota que queremos editar.
    mascota = get_object_or_404(
        Mascota,
        id=mascota_id
    )

    # Comprobar si ya tiene una adopción aprobada.
    tiene_adopcion_aprobada = SolicitudAdopcion.objects.filter(
        mascota=mascota,
        estado='Aprobada'
    ).exists()

    if request.method == 'POST':

        formulario = MascotaForm(
            request.POST,
            request.FILES,
            instance=mascota
        )

        if formulario.is_valid():

            mascota_editada = formulario.save(
                commit=False
            )

            # Una mascota adoptada no puede volver a
            # estar disponible por una edición accidental.
            if tiene_adopcion_aprobada:
                mascota_editada.disponible = False

            mascota_editada.save()

            messages.success(
                request,
                f'Los datos de {mascota_editada.nombre} '
                'se actualizaron correctamente.'
            )

            return redirect('gestionar_mascotas')

    else:

        formulario = MascotaForm(
            instance=mascota
        )

    contexto = {
        'formulario': formulario,
        'mascota': mascota,
        'tiene_adopcion_aprobada': tiene_adopcion_aprobada,
    }

    return render(
        request,
        'mascotas/editar_mascota.html',
        contexto
    )


# ==========================================
# PANEL ADMINISTRATIVO - ELIMINAR MASCOTA
# ==========================================

@login_required(login_url='login')
def eliminar_mascota(request, mascota_id):

    # Solo los superusuarios pueden eliminar mascotas.
    if not request.user.is_superuser:

        raise PermissionDenied(
            'No tienes permiso para eliminar mascotas.'
        )

    # Buscar la mascota.
    mascota = get_object_or_404(
        Mascota,
        id=mascota_id
    )

    # Comprobar si tiene solicitudes de adopción.
    tiene_solicitudes = SolicitudAdopcion.objects.filter(
        mascota=mascota
    ).exists()

    # Nunca eliminar mascotas con historial de adopciones.
    if tiene_solicitudes:

        messages.error(
            request,
            'No puedes eliminar esta mascota porque '
            'tiene solicitudes de adopción registradas. '
            'Puedes marcarla como no disponible.'
        )

        return redirect('gestionar_mascotas')

    # Solo eliminar cuando el administrador confirme.
    if request.method == 'POST':

        nombre_mascota = mascota.nombre

        mascota.delete()

        messages.success(
            request,
            f'La mascota {nombre_mascota} '
            'fue eliminada correctamente.'
        )

        return redirect('gestionar_mascotas')

    # Mostrar pantalla de confirmación.
    return render(
        request,
        'mascotas/eliminar_mascota.html',
        {
            'mascota': mascota
        }
    )


# ==========================================
# PANEL ADMINISTRATIVO - SOLICITUDES DE ADOPCIÓN
# ==========================================

@login_required(login_url='login')
def gestionar_solicitudes(request):

    # Solo los superusuarios pueden gestionar solicitudes.
    if not request.user.is_superuser:

        raise PermissionDenied(
            'No tienes permiso para gestionar solicitudes.'
        )

    # Obtener todas las solicitudes con sus usuarios y mascotas.
    solicitudes = SolicitudAdopcion.objects.select_related(
        'usuario',
        'mascota'
    ).order_by('-fecha')

    # Estadísticas por estado.
    solicitudes_pendientes = SolicitudAdopcion.objects.filter(
        estado='Pendiente'
    ).count()

    solicitudes_aprobadas = SolicitudAdopcion.objects.filter(
        estado='Aprobada'
    ).count()

    solicitudes_rechazadas = SolicitudAdopcion.objects.filter(
        estado='Rechazada'
    ).count()

    contexto = {
        'solicitudes': solicitudes,
        'solicitudes_pendientes': solicitudes_pendientes,
        'solicitudes_aprobadas': solicitudes_aprobadas,
        'solicitudes_rechazadas': solicitudes_rechazadas,
    }

    return render(
        request,
        'mascotas/gestionar_solicitudes.html',
        contexto
    )


# ==========================================
# PANEL ADMINISTRATIVO - APROBAR ADOPCIÓN
# ==========================================

@login_required(login_url='login')
def aprobar_solicitud(request, solicitud_id):

    # Solo los superusuarios pueden aprobar solicitudes.
    if not request.user.is_superuser:

        raise PermissionDenied(
            'No tienes permiso para aprobar solicitudes.'
        )

    # La aprobación solo se permite mediante POST.
    if request.method != 'POST':

        messages.error(
            request,
            'Debes confirmar la aprobación desde el panel.'
        )

        return redirect('gestionar_solicitudes')

    try:

        with transaction.atomic():

            # Localizar la solicitud.
            solicitud_inicial = get_object_or_404(
                SolicitudAdopcion,
                pk=solicitud_id
            )

            # Bloquear la mascota durante la operación
            # cuando la base de datos lo permita.
            mascota = get_object_or_404(
                Mascota.objects.select_for_update(),
                pk=solicitud_inicial.mascota_id
            )

            solicitud = get_object_or_404(
                SolicitudAdopcion.objects.select_for_update(),
                pk=solicitud_id
            )

            # Solo se pueden aprobar solicitudes pendientes.
            if solicitud.estado != 'Pendiente':

                messages.warning(
                    request,
                    'Solo se pueden aprobar solicitudes pendientes.'
                )

                return redirect('gestionar_solicitudes')

            # Verificar que no exista otra adopción aprobada.
            adopcion_existente = SolicitudAdopcion.objects.filter(
                mascota=mascota,
                estado='Aprobada'
            ).exists()

            if not mascota.disponible or adopcion_existente:

                messages.error(
                    request,
                    'La mascota ya no está disponible para adopción.'
                )

                return redirect('gestionar_solicitudes')

            # Aprobar la solicitud seleccionada.
            solicitud.estado = 'Aprobada'
            solicitud.save(
                update_fields=['estado']
            )

            # Marcar la mascota como no disponible.
            mascota.disponible = False
            mascota.save(
                update_fields=['disponible']
            )

            # Rechazar las demás solicitudes pendientes
            # para evitar múltiples adopciones.
            SolicitudAdopcion.objects.filter(
                mascota=mascota,
                estado='Pendiente'
            ).exclude(
                pk=solicitud.pk
            ).update(
                estado='Rechazada'
            )

    except IntegrityError:

        messages.error(
            request,
            'No se pudo aprobar la solicitud. '
            'Comprueba si ya existe una adopción aprobada.'
        )

        return redirect('gestionar_solicitudes')

    messages.success(
        request,
        f'Adopción de {mascota.nombre} aprobada correctamente.'
    )

    return redirect('gestionar_solicitudes')


# ==========================================
# PANEL ADMINISTRATIVO - RECHAZAR ADOPCIÓN
# ==========================================

@login_required(login_url='login')
def rechazar_solicitud(request, solicitud_id):

    # Solo los superusuarios pueden rechazar solicitudes.
    if not request.user.is_superuser:

        raise PermissionDenied(
            'No tienes permiso para rechazar solicitudes.'
        )

    # El rechazo solo se permite mediante POST.
    if request.method != 'POST':

        messages.error(
            request,
            'Debes confirmar el rechazo desde el panel.'
        )

        return redirect('gestionar_solicitudes')

    with transaction.atomic():

        solicitud = get_object_or_404(
            SolicitudAdopcion.objects.select_for_update(),
            pk=solicitud_id
        )

        # Solo rechazar solicitudes pendientes.
        if solicitud.estado != 'Pendiente':

            messages.warning(
                request,
                'Solo se pueden rechazar solicitudes pendientes.'
            )

            return redirect('gestionar_solicitudes')

        # Actualizar el estado.
        solicitud.estado = 'Rechazada'
        solicitud.save(
            update_fields=['estado']
        )

    messages.success(
        request,
        'La solicitud fue rechazada correctamente.'
    )

    return redirect('gestionar_solicitudes')



# ==========================================
# PÁGINA PÚBLICA DE RESEÑAS
# ==========================================

def ver_resenas(request):

    # Obtener todas las reseñas publicadas.
    # select_related permite consultar los datos
    # del usuario sin hacer consultas adicionales
    # por cada reseña.

    resenas = Resena.objects.select_related(
        'usuario'
    ).order_by('-fecha')

    # Enviar las reseñas a nuestra plantilla HTML.
    contexto = {
        'resenas': resenas
    }

    return render(
        request,
        'mascotas/resenas.html',
        contexto
    )



# ==========================================
# PANEL ADMINISTRATIVO - GESTIONAR RESEÑAS
# ==========================================

@login_required(login_url='login')
def gestionar_resenas(request):

    # Solo los superusuarios pueden acceder.
    if not request.user.is_superuser:

        raise PermissionDenied(
            'No tienes permiso para gestionar reseñas.'
        )

    # Obtener todas las reseñas con sus autores.
    resenas = Resena.objects.select_related(
        'usuario'
    ).order_by('-fecha')

    # Estadísticas generales.
    total_resenas = Resena.objects.count()

    resenas_5_estrellas = Resena.objects.filter(
        calificacion=5
    ).count()

    resenas_4_estrellas = Resena.objects.filter(
        calificacion=4
    ).count()

    resenas_bajas = Resena.objects.filter(
        calificacion__lte=3
    ).count()

    contexto = {
        'resenas': resenas,
        'total_resenas': total_resenas,
        'resenas_5_estrellas': resenas_5_estrellas,
        'resenas_4_estrellas': resenas_4_estrellas,
        'resenas_bajas': resenas_bajas,
    }

    return render(
        request,
        'mascotas/gestionar_resenas.html',
        contexto
    )




# ==========================================
# PANEL ADMINISTRATIVO - GESTIONAR USUARIOS
# ==========================================

@login_required(login_url='login')
def gestionar_usuarios(request):

    # Permitir acceso únicamente a superusuarios.
    if not request.user.is_superuser:
        raise PermissionDenied(
            'No tienes permiso para gestionar usuarios.'
        )

    # Obtener únicamente las cuentas de usuarios normales.
    usuarios = User.objects.filter(
        is_staff=False,
        is_superuser=False
    ).annotate(
        total_solicitudes=Count(
            'solicitudadopcion',
            distinct=True
        ),
        total_resenas_usuario=Count(
            'resena',
            distinct=True
        )
    ).order_by('-date_joined')

    # Estadísticas generales.
    total_usuarios = usuarios.count()

    usuarios_activos = usuarios.filter(
        is_active=True
    ).count()

    usuarios_inactivos = usuarios.filter(
        is_active=False
    ).count()

    contexto = {
        'usuarios': usuarios,
        'total_usuarios': total_usuarios,
        'usuarios_activos': usuarios_activos,
        'usuarios_inactivos': usuarios_inactivos,
    }

    return render(
        request,
        'mascotas/gestionar_usuarios.html',
        contexto
    )


# ==========================================
# EDITAR PERFIL DEL USUARIO
# ==========================================

@login_required(login_url='login')
def editar_perfil(request):

    # Los administradores no utilizan el perfil normal.
    if request.user.is_staff or request.user.is_superuser:
        return redirect('panel_administrador')

    if request.method == 'POST':

        nombre = request.POST.get(
            'first_name', ''
        ).strip()

        apellidos = request.POST.get(
            'last_name', ''
        ).strip()

        correo = request.POST.get(
            'email', ''
        ).strip()

        # Validar nombre.
        if not nombre:
            messages.error(
                request,
                'Debes ingresar tu nombre.'
            )

        # Validar apellidos.
        elif not apellidos:
            messages.error(
                request,
                'Debes ingresar tus apellidos.'
            )

        # Validar correo electrónico.
        elif not correo:
            messages.error(
                request,
                'Debes ingresar tu correo electrónico.'
            )

        else:

            from django.core.validators import validate_email
            from django.core.exceptions import ValidationError

            try:
                validate_email(correo)

            except ValidationError:
                messages.error(
                    request,
                    'Ingresa un correo electrónico válido.'
                )

            else:

                # Evitar que dos usuarios tengan
                # el mismo correo electrónico.
                correo_existente = User.objects.filter(
                    email__iexact=correo
                ).exclude(
                    pk=request.user.pk
                ).exists()

                if correo_existente:

                    messages.error(
                        request,
                        'Este correo electrónico ya está registrado.'
                    )

                else:

                    # Guardar los cambios del usuario.
                    request.user.first_name = nombre
                    request.user.last_name = apellidos
                    request.user.email = correo

                    request.user.save(
                        update_fields=[
                            'first_name',
                            'last_name',
                            'email'
                        ]
                    )

                    messages.success(
                        request,
                        '¡Tu perfil fue actualizado correctamente!'
                    )

                    return redirect('perfil')

    return render(
        request,
        'mascotas/editar_perfil.html'
    )



# ==========================================
# CAMBIAR CONTRASEÑA DEL USUARIO
# ==========================================

@login_required(login_url='login')
def cambiar_contrasena(request):

    # Los administradores no utilizan
    # esta sección del perfil normal.
    if request.user.is_staff or request.user.is_superuser:
        return redirect('panel_administrador')

    if request.method == 'POST':

        formulario = PasswordChangeForm(
            user=request.user,
            data=request.POST
        )

        if formulario.is_valid():

            # Guarda la nueva contraseña de forma segura.
            usuario = formulario.save()

            # Mantiene la sesión iniciada después
            # de cambiar la contraseña.
            update_session_auth_hash(
                request,
                usuario
            )

            messages.success(
                request,
                '¡Tu contraseña fue actualizada correctamente!'
            )

            return redirect('perfil')

    else:

        formulario = PasswordChangeForm(
            user=request.user
        )

    return render(
        request,
        'mascotas/cambiar_contrasena.html',
        {
            'formulario': formulario
        }
    )



# ==========================================
# PÁGINA PÚBLICA: NOSOTROS
# ==========================================

def nosotros(request):
    return render(request, 'mascotas/nosotros.html')



# ==========================================
# CHAT PRIVADO DEL USUARIO
# ==========================================

@login_required(login_url='login')
def chat_usuario(request):

    # Los administradores utilizan su propia bandeja.
    if request.user.is_staff or request.user.is_superuser:
        return redirect('bandeja_mensajes')

    # Enviar un mensaje nuevo.
    if request.method == 'POST':

        contenido = request.POST.get(
            'contenido', ''
        ).strip()

        if not contenido:
            messages.error(
                request,
                'No puedes enviar un mensaje vacío.'
            )

        elif len(contenido) > 2000:
            messages.error(
                request,
                'El mensaje no puede superar los 2000 caracteres.'
            )

        else:
            MensajeChat.objects.create(
                usuario=request.user,
                remitente='usuario',
                contenido=contenido
            )

            messages.success(
                request,
                '¡Mensaje enviado correctamente!'
            )

        return redirect('chat_usuario')

    # Marcar como leídas las respuestas del administrador.
    MensajeChat.objects.filter(
        usuario=request.user,
        remitente='administrador',
        leido=False
    ).update(leido=True)

    # Consultar únicamente los mensajes propios.
    conversacion = MensajeChat.objects.filter(
        usuario=request.user
    ).order_by('fecha', 'id')

    return render(
        request,
        'mascotas/chat_usuario.html',
        {
            'conversacion': conversacion
        }
    )


# ==========================================
# BANDEJA DE MENSAJES DEL ADMINISTRADOR
# ==========================================

@login_required(login_url='login')
def bandeja_mensajes(request):

    # Solo el superusuario puede acceder.
    if not request.user.is_superuser:
        raise PermissionDenied(
            'No tienes permiso para consultar los mensajes.'
        )

    # Obtener únicamente usuarios que tienen mensajes.
    usuarios = User.objects.filter(
        is_staff=False,
        is_superuser=False,
        mensajes_chat__isnull=False
    ).distinct().order_by('username')

    conversaciones = []

    for usuario in usuarios:

        mensajes_usuario = MensajeChat.objects.filter(
            usuario=usuario
        )

        ultimo_mensaje = mensajes_usuario.order_by(
            '-fecha', '-id'
        ).first()

        pendientes = mensajes_usuario.filter(
            remitente='usuario',
            leido=False
        ).count()

        conversaciones.append({
            'usuario': usuario,
            'ultimo_mensaje': ultimo_mensaje,
            'pendientes': pendientes,
        })

    # Mostrar primero las conversaciones más recientes.
    conversaciones.sort(
        key=lambda item: (
            item['ultimo_mensaje'].fecha,
            item['ultimo_mensaje'].id
        ),
        reverse=True
    )

    total_pendientes = MensajeChat.objects.filter(
        remitente='usuario',
        leido=False,
        usuario__is_staff=False,
        usuario__is_superuser=False
    ).count()

    return render(
        request,
        'mascotas/bandeja_mensajes.html',
        {
            'conversaciones': conversaciones,
            'total_pendientes': total_pendientes,
        }
    )


# ==========================================
# CHAT DEL ADMINISTRADOR CON UN USUARIO
# ==========================================

@login_required(login_url='login')
def chat_administrador(request, usuario_id):

    # Solo el superusuario puede responder.
    if not request.user.is_superuser:
        raise PermissionDenied(
            'No tienes permiso para responder mensajes.'
        )

    # Buscar únicamente cuentas de usuarios normales.
    usuario_chat = get_object_or_404(
        User,
        pk=usuario_id,
        is_staff=False,
        is_superuser=False
    )

    # Evitar abrir conversaciones inexistentes.
    if not MensajeChat.objects.filter(
        usuario=usuario_chat
    ).exists():
        messages.warning(
            request,
            'Este usuario todavía no tiene una conversación.'
        )
        return redirect('bandeja_mensajes')

    # Enviar respuesta.
    if request.method == 'POST':

        contenido = request.POST.get(
            'contenido', ''
        ).strip()

        if not contenido:
            messages.error(
                request,
                'No puedes enviar una respuesta vacía.'
            )

        elif len(contenido) > 2000:
            messages.error(
                request,
                'La respuesta no puede superar los 2000 caracteres.'
            )

        else:
            MensajeChat.objects.create(
                usuario=usuario_chat,
                remitente='administrador',
                contenido=contenido
            )

            messages.success(
                request,
                '¡Respuesta enviada correctamente!'
            )

        return redirect(
            'chat_administrador',
            usuario_id=usuario_chat.id
        )

    # Marcar como leídos los mensajes del usuario.
    MensajeChat.objects.filter(
        usuario=usuario_chat,
        remitente='usuario',
        leido=False
    ).update(leido=True)

    # Mostrar conversación completa.
    conversacion = MensajeChat.objects.filter(
        usuario=usuario_chat
    ).order_by('fecha', 'id')

    return render(
        request,
        'mascotas/chat_administrador.html',
        {
            'usuario_chat': usuario_chat,
            'conversacion': conversacion,
        }
    )











 

 

 

 

 

 

 

 

 

 

 
