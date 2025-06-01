from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from ads import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.base, name='base'),

    # Встроенные представления для входа/выхода и смены пароля
    path('accounts/', include('django.contrib.auth.urls')),

    # Регистрация (если нужна) — см. следующий пункт
    path('accounts/register/', views.register, name='register'),
    path('accounts/profile/', views.profile, name='profile'),

    # Объявления
    path('ads/', views.ad_list, name='ad_list'),
    path('ads/create/', views.create_ad, name='create_ad'),
    path('ads/<int:ad_id>/', views.ad_detail, name='ad_detail'),
    path('ads/<int:ad_id>/edit/', views.edit_ad, name='edit_ad'),
    path('ads/<int:ad_id>/delete/', views.delete_ad, name='delete_ad'),

    # Предложения обмена
    path('ads/<int:ad_receiver_id>/propose/', views.create_proposal, name='create_proposal'),
    path('proposals/', views.proposal_list, name='proposal_list'),
    path('proposals/<int:proposal_id>/', views.proposal_detail, name='proposal_detail'),
    path(
        'proposals/<int:proposal_id>/update/<str:new_status>/',
        views.update_proposal,
        name='update_proposal'
    ),
    path(
        'proposals/<int:proposal_id>/delete/',
        views.delete_proposal,
        name='delete_proposal'
    ),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
