from django.urls import path
from .views import lista_jucatori, detalii_jucator, welcome_page
from . import views

urlpatterns = [
    path('', welcome_page, name='welcome'),
    path('lista/', lista_jucatori, name='lista_jucatori'),
    path('<int:jucator_id>/', detalii_jucator, name='detalii_jucator'),
    path('cauta/', views.cauta_jucator, name='cauta_jucator'),
    path('magazin/', views.magazin_rachete, name='magazin_rachete'),
    path('magazin/racheta/<slug:slug>/', views.detalii_racheta, name='detalii_racheta'),
    path('cos/', views.vizualizare_cos, name='vizualizare_cos'),
    path('cos/adauga/', views.adauga_in_cos, name='adauga_in_cos'),
    path('cos/actualizeaza/', views.actualizeaza_cos, name='actualizeaza_cos'),
    path('cos/elimina/', views.elimina_din_cos, name='elimina_din_cos'),
    path('abonamente/', views.abonamente, name='abonamente'),
    path('abonamente/<str:tip>/', views.abonament_formular, name='abonament_formular'),
    path('procesare-plata/', views.procesare_plata, name='procesare_plata'),
]