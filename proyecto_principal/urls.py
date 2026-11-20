"""
URL configuration for proyecto_principal project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from app_parqueadero.auth_api import CurrentUserView, RoleTokenObtainPairView
from app_parqueadero.views import (
    BitacoraListView,
    ConsultaEstadoVehiculoView,
    EstacionamientoEntradaView,
    EstacionamientoListView,
    VehiculoListCreateView,
)
from app_parqueadero.web_views import demo_login

urlpatterns = [
    path('', demo_login, name='demo_login'),
    path('admin/', admin.site.urls),
    path('api/auth/token/', RoleTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/auth/me/', CurrentUserView.as_view(), name='current_user'),
    # Endpoints de negocio (Criterios 2.2 a 2.4)
    path('api/vehiculos/', VehiculoListCreateView.as_view(), name='api_vehiculos'),
    path('api/estacionamientos/', EstacionamientoListView.as_view(), name='api_estacionamientos'),
    path('api/estacionamientos/entrada/', EstacionamientoEntradaView.as_view(), name='api_entrada_automatica'),
    path('api/estacionamientos/estado/<str:placa>/', ConsultaEstadoVehiculoView.as_view(), name='api_consulta_estado'),
    path('api/bitacora/', BitacoraListView.as_view(), name='api_bitacora'),
]
