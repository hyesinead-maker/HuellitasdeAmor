
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import Mascota, Resena, SolicitudAdopcion


# ==========================================
# FORMULARIO DE REGISTRO DE USUARIOS
# ==========================================

class RegistroUsuarioForm(UserCreationForm):

    first_name = forms.CharField(
        label='Nombre',
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Escribe tu nombre'
        })
    )

    last_name = forms.CharField(
        label='Apellidos',
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Escribe tus apellidos'
        })
    )

    email = forms.EmailField(
        label='Correo electrónico',
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'ejemplo@correo.com'
        })
    )

    class Meta:
        model = User

        fields = [
            'first_name',
            'last_name',
            'username',
            'email',
            'password1',
            'password2'
        ]

        labels = {
            'username': 'Nombre de usuario'
        }

        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Elige un nombre de usuario'
            })
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for nombre_campo in self.fields:
            campo = self.fields[nombre_campo]
            campo.widget.attrs['class'] = 'form-control'

    def clean_email(self):
        email = self.cleaned_data['email'].strip().lower()

        if User.objects.filter(
            email__iexact=email
        ).exists():
            raise forms.ValidationError(
                'Este correo electrónico ya está registrado.'
            )

        return email


# ==========================================
# FORMULARIO DE RESEÑAS
# ==========================================

class ResenaForm(forms.ModelForm):

    class Meta:
        model = Resena

        fields = [
            'titulo',
            'comentario',
            'calificacion'
        ]

        labels = {
            'titulo': 'Título de tu reseña',
            'comentario': 'Cuéntanos tu experiencia',
            'calificacion': 'Calificación'
        }

        widgets = {
            'titulo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ejemplo: Una experiencia maravillosa'
            }),

            'comentario': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Escribe aquí tu experiencia...',
                'rows': 5
            }),

            'calificacion': forms.Select(attrs={
                'class': 'form-control'
            })
        }


# ==========================================
# FORMULARIO ADMINISTRATIVO DE ADOPCIONES
# ==========================================

class SolicitudAdopcionAdminForm(forms.ModelForm):

    class Meta:
        model = SolicitudAdopcion
        fields = '__all__'

    def clean_estado(self):

        estado = self.cleaned_data.get('estado')

        if estado == 'Aprobada':

            otra_aprobada = SolicitudAdopcion.objects.filter(
                mascota=self.instance.mascota,
                estado='Aprobada'
            ).exclude(
                pk=self.instance.pk
            ).exists()

            if otra_aprobada:
                raise forms.ValidationError(
                    'Esta mascota ya tiene una solicitud '
                    'de adopción aprobada. No puedes '
                    'aprobar otra solicitud.'
                )

            if (
                self.instance.estado != 'Aprobada'
                and not self.instance.mascota.disponible
            ):
                raise forms.ValidationError(
                    'Esta mascota ya no está disponible '
                    'para adopción.'
                )

        return estado


# ==========================================
# FORMULARIO PARA ADMINISTRAR MASCOTAS
# ==========================================

class MascotaForm(forms.ModelForm):

    class Meta:
        model = Mascota

        fields = [
            'nombre',
            'especie',
            'raza',
            'edad',
            'descripcion',
            'foto',
            'disponible'
        ]

        labels = {
            'nombre': 'Nombre de la mascota',
            'especie': 'Especie',
            'raza': 'Raza',
            'edad': 'Edad (en meses)',
            'descripcion': 'Descripción de la mascota',
            'foto': 'Fotografía',
            'disponible': 'Disponible para adopción'
        }

        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ejemplo: Max'
            }),

            'especie': forms.Select(attrs={
                'class': 'form-control'
            }),

            'raza': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ejemplo: Mestizo'
            }),

            'edad': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0,
                'placeholder': 'Ejemplo: 12'
            }),

            'descripcion': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': (
                    'Describe su personalidad, '
                    'cuidados y características...'
                )
            }),

            'foto': forms.ClearableFileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),

            'disponible': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }

    def clean_edad(self):
        edad = self.cleaned_data.get('edad')

        if edad is not None and edad < 0:
            raise forms.ValidationError(
                'La edad no puede ser negativa.'
            )

        return edad


