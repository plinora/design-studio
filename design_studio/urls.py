from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from core import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('register/', views.register, name='register'),

    # Каталог
    path('services/', views.services_list, name='services_list'),
    path('services/<int:service_id>/', views.service_detail, name='service_detail'),

    # Объявления
    path('create-service/', views.create_service, name='create_service'),
    path('my-services/', views.my_services, name='my_services'),
    path('edit-service/<int:service_id>/', views.edit_service, name='edit_service'),
    path('delete-service/<int:service_id>/', views.delete_service, name='delete_service'),
    path('delete-service-image/<int:image_id>/', views.delete_service_image, name='delete_service_image'),

    # Избранное
    path('favorites/', views.favorites_list, name='favorites_list'),
    path('add-favorite/<int:service_id>/', views.add_favorite, name='add_favorite'),
    path('remove-favorite/<int:service_id>/', views.remove_favorite, name='remove_favorite'),

    # Жалобы (админ)
    path('complaints/', views.complaints_list, name='complaints_list'),
    path('complaint-action/<int:complaint_id>/<str:action>/', views.complaint_action, name='complaint_action'),

    # Чаты
    path('chats/', views.chats_list, name='chats_list'),
    path('chat/<int:designer_id>/', views.chat_detail, name='chat_detail'),
    path('create-order-from-chat/<int:designer_id>/', views.create_order_from_chat, name='create_order_from_chat'),
    path('add-balance/', views.add_balance, name='add_balance'),
    path('cancel-order/<int:order_id>/', views.cancel_order, name='cancel_order'),
    # Заказы
    path('my-orders/', views.my_orders, name='my_orders'),
    path('update-order-status/<int:order_id>/<str:status>/', views.update_order_status, name='update_order_status'),
    path('delete-chat/<int:designer_id>/', views.delete_chat, name='delete_chat'),

    # Отзывы
    path('leave-review/<int:order_id>/', views.leave_review, name='leave_review'),

    # Профиль (только для клиента и дизайнера)
    path('profile/', views.edit_profile, name='profile'),

    path('complain/<int:service_id>/', views.complain_service, name='complain'),
    path('withdraw-balance/', views.withdraw_balance, name='withdraw_balance'),

    path('respond/<int:service_id>/', views.respond_to_service, name='respond_to_service'),
    path('pay-order/<int:order_id>/', views.pay_order, name='pay_order'),
    path('start-work/<int:order_id>/', views.start_work, name='start_work'),
    path('send-project/<int:order_id>/', views.send_project, name='send_project'),
    path('confirm-client/<int:order_id>/', views.confirm_complete_client, name='confirm_complete_client'),
    path('confirm-designer/<int:order_id>/', views.confirm_complete_designer, name='confirm_complete_designer'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)