from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils.timezone import now
from accounts.models import User as CustomUser
from projects.models import Service, ServiceImage, Favorite, Complaint, Order, Message, Review
from decimal import Decimal


def home(request):
    return render(request, 'home.html')


def register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        role = request.POST.get('role')
        company = request.POST.get('company', '')
        phone = request.POST.get('phone', '')
        gender = request.POST.get('gender', '')
        birth_date = request.POST.get('birth_date', None)
        age = request.POST.get('age', None)

        if password1 != password2:
            messages.error(request, 'Пароли не совпадают')
            return render(request, 'register.html')

        if CustomUser.objects.filter(username=username).exists():
            messages.error(request, 'Пользователь с таким именем уже существует')
            return render(request, 'register.html')

        if CustomUser.objects.filter(email=email).exists():
            messages.error(request, 'Пользователь с таким email уже существует')
            return render(request, 'register.html')

        user = CustomUser.objects.create_user(
            username=username,
            email=email,
            password=password1,
            role=role,
            company=company,
            phone=phone,
        )
        user.gender = gender
        if birth_date:
            user.birth_date = birth_date
        if age:
            user.age = age
        user.save()

        login(request, user)
        messages.success(request, f'Добро пожаловать, {username}!')
        return redirect('home')

    return render(request, 'register.html')


@login_required
def services_list(request):
    services = Service.objects.filter(is_active=True)

    # Фильтр по сфере
    sphere = request.GET.get('sphere')
    if sphere:
        services = services.filter(sphere=sphere)

    unread_count = Message.objects.filter(receiver=request.user, is_read=False).count()
    return render(request, 'services.html', {'services': services, 'unread_count': unread_count})


@login_required
def service_detail(request, service_id):
    service = get_object_or_404(Service, id=service_id)
    favorites_ids = []
    if request.user.role == 'client':
        favorites_ids = Favorite.objects.filter(client=request.user).values_list('service_id', flat=True)
    unread_count = Message.objects.filter(receiver=request.user, is_read=False).count()
    return render(request, 'service_detail.html', {
        'service': service,
        'favorites_ids': list(favorites_ids),
        'unread_count': unread_count,
    })


@login_required
def create_service(request):
    if request.user.role != 'designer':
        messages.error(request, 'Только дизайнеры могут создавать объявления')
        return redirect('home')

    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        sphere = request.POST.get('sphere')
        price = request.POST.get('price', 0)

        service = Service.objects.create(
            designer=request.user,
            title=title,
            description=description,
            sphere=sphere,
            price=price,
        )
        images = request.FILES.getlist('images')
        for img in images[:3]:
            ServiceImage.objects.create(service=service, image=img)

        messages.success(request, 'Объявление создано!')
        return redirect('my_services')

    unread_count = Message.objects.filter(receiver=request.user, is_read=False).count()
    return render(request, 'create_service.html', {'unread_count': unread_count})


@login_required
def my_services(request):
    if request.user.role != 'designer':
        messages.error(request, 'Эта страница только для дизайнеров')
        return redirect('home')

    services = Service.objects.filter(designer=request.user)
    unread_count = Message.objects.filter(receiver=request.user, is_read=False).count()
    return render(request, 'my_services.html', {'services': services, 'unread_count': unread_count})


@login_required
def edit_service(request, service_id):
    service = get_object_or_404(Service, id=service_id, designer=request.user)

    if request.method == 'POST':
        service.title = request.POST.get('title')
        service.description = request.POST.get('description')
        service.sphere = request.POST.get('sphere')
        service.price = request.POST.get('price', 0)
        service.save()

        images = request.FILES.getlist('images')
        for img in images[:3]:
            ServiceImage.objects.create(service=service, image=img)

        messages.success(request, 'Объявление обновлено!')
        return redirect('service_detail', service_id=service.id)

    unread_count = Message.objects.filter(receiver=request.user, is_read=False).count()
    return render(request, 'edit_service.html', {'service': service, 'unread_count': unread_count})


@login_required
def delete_service(request, service_id):
    service = get_object_or_404(Service, id=service_id)

    if request.user != service.designer and not request.user.is_admin:
        messages.error(request, 'Недостаточно прав для удаления')
        return redirect('service_detail', service_id=service.id)

    if request.method == 'POST':
        service.delete()
        messages.success(request, 'Объявление удалено!')
        return redirect('my_services' if request.user.role == 'designer' else 'services_list')

    unread_count = Message.objects.filter(receiver=request.user, is_read=False).count()
    return render(request, 'delete_service.html', {'service': service, 'unread_count': unread_count})


@login_required
def delete_service_image(request, image_id):
    image = get_object_or_404(ServiceImage, id=image_id)
    service = image.service
    if request.user != service.designer:
        messages.error(request, 'Недостаточно прав')
        return redirect('home')
    image.delete()
    messages.success(request, 'Фото удалено')
    return redirect('edit_service', service_id=service.id)


@login_required
def favorites_list(request):
    if request.user.role != 'client':
        messages.error(request, 'Избранное доступно только клиентам')
        return redirect('home')

    favorites = Favorite.objects.filter(client=request.user)
    unread_count = Message.objects.filter(receiver=request.user, is_read=False).count()
    return render(request, 'favorites.html', {'favorites': favorites, 'unread_count': unread_count})


@login_required
def add_favorite(request, service_id):
    if request.user.role != 'client':
        messages.error(request, 'Только клиенты могут добавлять в избранное')
        return redirect('home')

    service = get_object_or_404(Service, id=service_id)
    Favorite.objects.get_or_create(client=request.user, service=service)
    messages.success(request, 'Добавлено в избранное')
    return redirect('service_detail', service_id=service_id)


@login_required
def remove_favorite(request, service_id):
    if request.user.role != 'client':
        messages.error(request, 'Только клиенты могут удалять из избранного')
        return redirect('home')

    service = get_object_or_404(Service, id=service_id)
    Favorite.objects.filter(client=request.user, service=service).delete()
    messages.success(request, 'Удалено из избранного')
    return redirect('favorites_list')


@login_required
def complaints_list(request):
    if not request.user.is_admin:
        messages.error(request, 'Доступ только для администратора')
        return redirect('home')

    complaints = Complaint.objects.filter(is_reviewed=False).order_by('-created_at')
    unread_count = Message.objects.filter(receiver=request.user, is_read=False).count()
    return render(request, 'complaints_list.html', {'complaints': complaints, 'unread_count': unread_count})


@login_required
def complaint_action(request, complaint_id, action):
    if not request.user.is_admin:
        messages.error(request, 'Доступ только для администратора')
        return redirect('home')

    complaint = get_object_or_404(Complaint, id=complaint_id)

    if action == 'delete':
        complaint.service.delete()
        messages.success(request, 'Объявление удалено')
    elif action == 'reject':
        messages.success(request, 'Жалоба отклонена')
    else:
        messages.error(request, 'Неизвестное действие')
        return redirect('complaints_list')

    complaint.is_reviewed = True
    complaint.save()
    return redirect('complaints_list')


@login_required
def chats_list(request):
    user = request.user

    sent_to = Message.objects.filter(sender=user).values_list('receiver_id', flat=True)
    received_from = Message.objects.filter(receiver=user).values_list('sender_id', flat=True)
    chat_user_ids = set(sent_to) | set(received_from)
    chats = CustomUser.objects.filter(id__in=chat_user_ids)

    unread_count = Message.objects.filter(receiver=user, is_read=False).count()

    unread_chat_ids = []
    for chat in chats:
        if Message.objects.filter(sender=chat, receiver=user, is_read=False).exists():
            unread_chat_ids.append(chat.id)

    return render(request, 'chats_list.html', {
        'chats': chats,
        'unread_count': unread_count,
        'unread_chat_ids': unread_chat_ids,
        'now': now(),
    })


@login_required
def chat_detail(request, designer_id):
    designer = get_object_or_404(CustomUser, id=designer_id)

    if request.user.role == 'designer' and designer.is_admin:
        has_message_from_admin = Message.objects.filter(sender=designer, receiver=request.user).exists()
        if not has_message_from_admin:
            messages.error(request, 'Вы не можете начать чат с администратором')
            return redirect('chats_list')

    if request.user.role == 'designer' and not designer.is_admin:
        has_message = Message.objects.filter(receiver=request.user, sender=designer).exists()
        if not has_message:
            messages.error(request, 'Вы не можете начать чат первым')
            return redirect('chats_list')

    messages_list = Message.objects.filter(
        sender=request.user, receiver=designer
    ) | Message.objects.filter(
        sender=designer, receiver=request.user
    ).order_by('created_at')

    unread_messages = Message.objects.filter(receiver=request.user, sender=designer, is_read=False)
    unread_messages.update(is_read=True)

    order = None
    if request.user.role == 'client' and designer.role == 'designer':
        order = Order.objects.filter(client=request.user, designer=designer).first()
    elif request.user.role == 'designer' and designer.role == 'client':
        order = Order.objects.filter(client=designer, designer=request.user).first()

    if request.method == 'POST':
        text = request.POST.get('message', '').strip()
        file = request.FILES.get('file')
        image = request.FILES.get('image')

        if text or file or image:
            msg = Message.objects.create(
                sender=request.user,
                receiver=designer,
                text=text or '',
                order=order
            )
            if file:
                msg.file = file
            if image:
                msg.image = image
            msg.save()
            messages.success(request, 'Сообщение отправлено')
        return redirect('chat_detail', designer_id=designer_id)

    unread_count = Message.objects.filter(receiver=request.user, is_read=False).count()

    return render(request, 'chat_detail.html', {
        'designer': designer,
        'messages_list': messages_list,
        'order': order,
        'unread_count': unread_count,
        'now': now(),
    })


@login_required
def delete_chat(request, designer_id):
    designer = get_object_or_404(CustomUser, id=designer_id)
    Message.objects.filter(sender=request.user, receiver=designer).delete()
    Message.objects.filter(sender=designer, receiver=request.user).delete()
    messages.success(request, 'Чат удалён')
    return redirect('chats_list')


# ===== ОТКЛИК =====
@login_required
def respond_to_service(request, service_id):
    service = get_object_or_404(Service, id=service_id)

    if request.user.role != 'client':
        messages.error(request, 'Только клиенты могут откликаться')
        return redirect('home')

    existing_order = Order.objects.filter(client=request.user, service=service).first()
    if existing_order:
        messages.warning(request, 'Вы уже откликнулись на это объявление')
        return redirect('chat_detail', designer_id=service.designer.id)

    order = Order.objects.create(
        client=request.user,
        designer=service.designer,
        service=service,
        status='thinking',
        price=service.price,
    )

    Message.objects.create(
        sender=request.user,
        receiver=service.designer,
        text=f'{request.user.username} откликнулся на ваше объявление "{service.title}"',
        order=order
    )

    messages.success(request, 'Вы откликнулись на объявление!')
    return redirect('chat_detail', designer_id=service.designer.id)


# ===== ПОПОЛНЕНИЕ БАЛАНСА =====
@login_required
def add_balance(request):
    if request.method == 'POST':
        amount = request.POST.get('amount', 0)
        try:
            amount = Decimal(amount)
            if amount <= 0:
                messages.error(request, 'Сумма должна быть больше 0')
                return redirect('profile')
            user = request.user
            user.balance += amount
            user.save()
            messages.success(request, f'Баланс пополнен на {amount} ₽')
        except:
            messages.error(request, 'Введите корректную сумму')
        return redirect('profile')
    return redirect('profile')


# ===== ОПЛАТА ЗАКАЗА (списание с баланса) =====
@login_required
def pay_order(request, order_id):
    order = get_object_or_404(Order, id=order_id)

    if request.user != order.client:
        messages.error(request, 'Только клиент может оплатить заказ')
        return redirect('chat_detail', designer_id=order.designer.id)

    if order.status != 'thinking':
        messages.error(request, 'Нельзя оплатить этот заказ')
        return redirect('chat_detail', designer_id=order.designer.id)

    if request.user.balance < order.price:
        messages.error(request, 'Недостаточно средств на балансе. Пополните баланс.')
        return redirect('profile')

    # Списание с клиента
    request.user.balance -= order.price
    request.user.save()

    order.status = 'paid'
    order.save()

    messages.success(request, f'Заказ оплачен! С вашего баланса списано {order.price} ₽')
    return redirect('chat_detail', designer_id=order.designer.id)


# ===== НАЧАЛО РАБОТЫ =====
@login_required
def start_work(request, order_id):
    order = get_object_or_404(Order, id=order_id)

    if request.user != order.designer:
        messages.error(request, 'Только дизайнер может начать работу')
        return redirect('chat_detail', designer_id=order.client.id)

    if order.status != 'paid':
        messages.error(request, 'Нельзя начать работу над этим заказом')
        return redirect('chat_detail', designer_id=order.client.id)

    order.status = 'in_progress'
    order.save()
    messages.success(request, 'Вы начали работу над проектом!')
    return redirect('chat_detail', designer_id=order.client.id)


# ===== ОТПРАВКА ПРОЕКТА =====
@login_required
def send_project(request, order_id):
    order = get_object_or_404(Order, id=order_id)

    if request.user != order.designer:
        messages.error(request, 'Только дизайнер может отправить проект')
        return redirect('chat_detail', designer_id=order.client.id)

    if order.status != 'in_progress':
        messages.error(request, 'Нельзя отправить проект')
        return redirect('chat_detail', designer_id=order.client.id)

    if request.method == 'POST':
        result = request.POST.get('result', '').strip()
        files = request.FILES.getlist('files')

        if result or files:
            order.result = result
            order.status = 'ready'
            order.save()

            for file in files:
                Message.objects.create(
                    sender=request.user,
                    receiver=order.client,
                    text=f'Файл: {file.name}',
                    file=file,
                    order=order
                )

            messages.success(request, 'Проект отправлен клиенту!')
        else:
            messages.error(request, 'Добавьте описание или прикрепите файлы')
        return redirect('chat_detail', designer_id=order.client.id)

    return render(request, 'send_project.html', {'order': order})


# ===== ПОДТВЕРЖДЕНИЕ КЛИЕНТА =====
@login_required
def confirm_complete_client(request, order_id):
    order = get_object_or_404(Order, id=order_id)

    if request.user != order.client:
        messages.error(request, 'Только клиент может подтвердить выполнение')
        return redirect('chat_detail', designer_id=order.designer.id)

    if order.status != 'ready':
        messages.error(request, 'Нельзя подтвердить этот заказ')
        return redirect('chat_detail', designer_id=order.designer.id)

    order.client_confirmed = True
    order.save()

    if order.designer_confirmed:
        # Зачисляем деньги дизайнеру
        order.designer.balance += order.price
        order.designer.save()
        order.status = 'completed'
        order.save()
        messages.success(request, 'Заказ завершён! Деньги перечислены дизайнеру.')
    else:
        messages.success(request, 'Вы подтвердили выполнение. Ожидайте подтверждения от дизайнера.')

    return redirect('chat_detail', designer_id=order.designer.id)


# ===== ПОДТВЕРЖДЕНИЕ ДИЗАЙНЕРА =====
@login_required
def confirm_complete_designer(request, order_id):
    order = get_object_or_404(Order, id=order_id)

    if request.user != order.designer:
        messages.error(request, 'Только дизайнер может подтвердить выполнение')
        return redirect('chat_detail', designer_id=order.client.id)

    if order.status != 'ready':
        messages.error(request, 'Нельзя подтвердить этот заказ')
        return redirect('chat_detail', designer_id=order.client.id)

    order.designer_confirmed = True
    order.save()

    if order.client_confirmed:
        # Зачисляем деньги дизайнеру
        order.designer.balance += order.price
        order.designer.save()
        order.status = 'completed'
        order.save()
        messages.success(request, 'Заказ завершён! Деньги перечислены дизайнеру.')
    else:
        messages.success(request, 'Вы подтвердили выполнение. Ожидайте подтверждения от клиента.')

    return redirect('chat_detail', designer_id=order.client.id)


# ===== ОТМЕНА ЗАКАЗА (для обоих) =====
@login_required
def cancel_order(request, order_id):
    order = get_object_or_404(Order, id=order_id)

    # Проверяем, что пользователь — участник заказа
    if request.user != order.client and request.user != order.designer:
        messages.error(request, 'Вы не можете отменить этот заказ')
        return redirect('home')

    # Нельзя отменить уже завершённый или отменённый заказ
    if order.status in ['completed', 'cancelled']:
        messages.error(request, 'Этот заказ уже нельзя отменить')
        return redirect('chat_detail', designer_id=order.designer.id if request.user == order.client else order.client.id)

    # Если заказ был оплачен — возвращаем деньги клиенту
    if order.status in ['paid', 'in_progress', 'ready']:
        order.client.balance += order.price
        order.client.save()
        messages.info(request, f'Деньги в размере {order.price} ₽ возвращены на ваш баланс.')

    order.status = 'cancelled'
    order.save()

    messages.success(request, 'Заказ отменён')

    # Перенаправляем в чат с собеседником
    if request.user == order.client:
        return redirect('chat_detail', designer_id=order.designer.id)
    else:
        return redirect('chat_detail', designer_id=order.client.id)


# ===== СОЗДАНИЕ ЗАКАЗА ИЗ ЧАТА (старое) =====
@login_required
def create_order_from_chat(request, designer_id):
    designer = get_object_or_404(CustomUser, id=designer_id, role='designer')

    if request.user.role != 'client':
        messages.error(request, 'Только клиенты могут создавать заказы')
        return redirect('home')

    existing_order = Order.objects.filter(
        client=request.user,
        designer=designer,
        status__in=['paid', 'in_progress']
    )
    if existing_order.exists():
        messages.warning(request, 'У вас уже есть активный заказ с этим дизайнером')
        return redirect('chat_detail', designer_id=designer_id)

    order = Order.objects.create(
        client=request.user,
        designer=designer,
        service=None,
        status='paid',
        price=0
    )

    messages.success(request, f'Заказ #{order.id} создан! Обсудите детали с дизайнером.')
    return redirect('chat_detail', designer_id=designer_id)


# ===== МОИ ЗАКАЗЫ =====
@login_required
def my_orders(request):
    if request.user.is_admin:
        messages.error(request, 'Администратор не имеет доступа к заказам')
        return redirect('home')

    user = request.user
    if user.role == 'client':
        orders = Order.objects.filter(client=user)
    elif user.role == 'designer':
        orders = Order.objects.filter(designer=user)
    else:
        orders = Order.objects.none()

    unread_count = Message.objects.filter(receiver=request.user, is_read=False).count()
    return render(request, 'my_orders.html', {'orders': orders, 'unread_count': unread_count})


# ===== СТАРЫЙ UPDATE STATUS (не используется, но оставим) =====
@login_required
def update_order_status(request, order_id, status):
    if request.user.is_admin:
        messages.error(request, 'Администратор не может менять статус заказа')
        return redirect('home')

    order = get_object_or_404(Order, id=order_id, designer=request.user)
    if status in ['in_progress', 'completed']:
        order.status = status
        order.save()
        messages.success(request, f'Статус заказа обновлён: {order.get_status_display()}')
    return redirect('my_orders')


# ===== ОТЗЫВЫ =====
@login_required
def leave_review(request, order_id):
    if request.user.is_admin:
        messages.error(request, 'Администратор не может оставлять отзывы')
        return redirect('home')

    order = get_object_or_404(Order, id=order_id, client=request.user, status='completed')
    if request.method == 'POST':
        rating = request.POST.get('rating')
        text = request.POST.get('text')
        Review.objects.create(
            client=request.user,
            designer=order.designer,
            order=order,
            rating=rating,
            text=text
        )
        messages.success(request, 'Спасибо за отзыв!')
        return redirect('my_orders')

    unread_count = Message.objects.filter(receiver=request.user, is_read=False).count()
    return render(request, 'leave_review.html', {'order': order, 'unread_count': unread_count})


# ===== ПРОФИЛЬ =====
@login_required
def edit_profile(request):
    if request.user.is_admin:
        messages.error(request, 'Администратор не имеет профиля')
        return redirect('home')

    user = request.user

    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        birth_date = request.POST.get('birth_date')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')

        user.username = username
        user.email = email
        user.birth_date = birth_date if birth_date else None

        if password1 and password1 == password2:
            user.set_password(password1)
            messages.success(request, 'Пароль изменён. Войдите заново.')
            return redirect('login')
        elif password1 and password1 != password2:
            messages.error(request, 'Пароли не совпадают')
            return redirect('profile')

        user.save()
        messages.success(request, 'Данные обновлены!')
        return redirect('profile')

    unread_count = Message.objects.filter(receiver=request.user, is_read=False).count()
    return render(request, 'profile.html', {'user': user, 'unread_count': unread_count})


@login_required
def withdraw_balance(request):
    user = request.user
    if user.balance <= 0:
        messages.error(request, 'На вашем балансе нет средств для вывода')
        return redirect('profile')

    # Имитация вывода на карту
    user.balance = 0
    user.save()
    messages.success(request, 'Все средства успешно выведены на привязанную карту')
    return redirect('profile')


@login_required
def complain_service(request, service_id):
    service = get_object_or_404(Service, id=service_id)
    if request.method == 'POST':
        reason = request.POST.get('reason', '')
        Complaint.objects.create(service=service, user=request.user, reason=reason)
        messages.success(request, 'Жалоба отправлена администратору')
        return redirect('service_detail', service_id=service.id)

    unread_count = Message.objects.filter(receiver=request.user, is_read=False).count()
    return render(request, 'complain.html', {'service': service, 'unread_count': unread_count})