from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import HttpResponseForbidden, HttpResponseBadRequest
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
from .forms import ProfileForm
from django.contrib.auth import update_session_auth_hash
from django.contrib import messages

from .models import Ad, ExchangeProposal
from .forms import AdForm, ExchangeProposalForm


def ad_list(request):
    q = request.GET.get('q', '')
    category = request.GET.get('category', '')
    condition = request.GET.get('condition', '')

    qs = Ad.objects.all()

    if q:
        qs = qs.filter(Q(title__icontains=q) | Q(description__icontains=q))

    if category:
        qs = qs.filter(category=category)
    if condition:
        qs = qs.filter(condition=condition)

    paginator   = Paginator(qs.order_by('-created_at'), 10)
    page_number = request.GET.get('page')
    page_obj    = paginator.get_page(page_number)

    return render(request, 'ads/ad_list.html', {
        'page_obj': page_obj,
        'q':         q,
        'category':  category,
        'condition': condition,
    })


def ad_detail(request, ad_id):
    ad = get_object_or_404(Ad, id=ad_id)
    return render(request, 'ads/ad_detail.html', {'ad': ad})


@login_required
def create_ad(request):
    if request.method == "POST":
        form = AdForm(request.POST, request.FILES)
        if form.is_valid():
            ad = form.save(commit=False)
            ad.user = request.user
            ad.save()
            messages.success(request, 'Объявление успешно создано.') 
            return redirect('ad_detail', ad_id=ad.id)
        else:
            messages.error(request, 'Пожалуйста, исправьте ошибки в форме создания объявления.')
    else:
        form = AdForm()
    return render(request, 'ads/create_ad.html', {'form': form})


@login_required
def edit_ad(request, ad_id):
    ad = get_object_or_404(Ad, id=ad_id, user=request.user)
    if request.method == "POST":
        form = AdForm(request.POST, request.FILES, instance=ad)
        if form.is_valid():
            form.save()
            messages.success(request, 'Объявление успешно обновлено.')
            return redirect('ad_detail', ad_id=ad.id)
        else:
            messages.error(request, 'Пожалуйста, исправьте ошибки в форме редактирования объявления.')
    else:
        form = AdForm(instance=ad)
    return render(request, 'ads/edit_ad.html', {'form': form, 'ad': ad})


@login_required
def delete_ad(request, ad_id):
    ad = get_object_or_404(Ad, id=ad_id, user=request.user)
    if request.method == 'POST':
        ad.delete()
        messages.success(request, 'Объявление удалено.')
        return redirect('ad_list')
    return render(request, 'ads/confirm_delete.html', {'ad': ad})


# 6. Список предложений обмена с фильтрацией + пагинация
@login_required
def proposal_list(request):
    # Берём только предложения, где текущий пользователь — отправитель или получатель
    qs = ExchangeProposal.objects.filter(
        Q(ad_sender__user=request.user) |
        Q(ad_receiver__user=request.user)
    )

    # Дальнейшая фильтрация по GET-параметрам (по желанию)
    sender   = request.GET.get('sender', '')
    receiver = request.GET.get('receiver', '')
    status   = request.GET.get('status', '')

    if sender:
        qs = qs.filter(ad_sender__id=sender)
    if receiver:
        qs = qs.filter(ad_receiver__id=receiver)
    if status:
        qs = qs.filter(status=status)

    # Пагинация
    paginator   = Paginator(qs.order_by('-created_at'), 10)
    page_number = request.GET.get('page')
    page_obj    = paginator.get_page(page_number)

    return render(request, 'ads/proposal_list.html', {
        'page_obj':  page_obj,
        'sender':    sender,
        'receiver':  receiver,
        'status':    status,
    })


# 7. Создание предложения обмена
@login_required
def create_proposal(request, ad_receiver_id):
    ad_receiver = get_object_or_404(Ad, id=ad_receiver_id)

    if request.method == 'POST':
        form = ExchangeProposalForm(request.POST, user=request.user)
        if form.is_valid():
            proposal = form.save(commit=False)
            proposal.ad_receiver = ad_receiver
            proposal.status      = 'pending'
            proposal.save()
            messages.success(request, 'Предложение обмена отправлено.')
            return redirect('proposal_list')
        else:
            messages.error(request, 'Пожалуйста, выберите своё объявление и заполните комментарий.')
    else:
        form = ExchangeProposalForm(user=request.user)

    return render(request, 'ads/create_proposal.html', {
        'form':        form,
        'ad_receiver': ad_receiver,
    })


# 8. Обновление статуса предложения (только получатель)
@login_required
def update_proposal(request, proposal_id, new_status):
    proposal = get_object_or_404(ExchangeProposal, id=proposal_id)

    # уже обработано?
    if proposal.status != 'pending':
        messages.warning(request, 'Это предложение уже обработано и не может быть изменено.')
        return HttpResponseBadRequest("Это предложение уже обработано и больше не подлежит изменению")

    # только владелец ad_receiver может менять статус
    if request.user != proposal.ad_receiver.user:
        messages.error(request, 'У вас нет прав на изменение этого предложения.')  
        return HttpResponseForbidden("Нет прав")

    # проверяем, что новый статус валиден
    valid_statuses = dict(ExchangeProposal.STATUS_CHOICES)
    if new_status not in valid_statuses:
        messages.error(request, 'Неверный статус предложения.')
        return HttpResponseBadRequest("Неверный статус")

    proposal.status = new_status
    proposal.save()
    return redirect('proposal_detail', proposal_id=proposal.id)



# 9. Детальный просмотр предложения
@login_required
def proposal_detail(request, proposal_id):
    prop = get_object_or_404(ExchangeProposal, id=proposal_id)
    return render(request, 'ads/proposal_detail.html', {'proposal': prop})


def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Регистрация прошла успешно. Войдите в систему.') 
            return redirect('login')  # перенаправим на форму логина
        else:
            messages.error(request, 'Пожалуйста, исправьте ошибки в форме регистрации.')
    else:
        form = UserCreationForm()
    return render(request, 'registration/register.html', {'form': form})


@login_required
def profile(request):
    user = request.user

    if request.method == 'POST':
        # какая кнопка нажата?
        if 'profile_submit' in request.POST:
            profile_form = ProfileForm(request.POST, instance=user)
            password_form = PasswordChangeForm(user)
            if profile_form.is_valid():
                profile_form.save()
                messages.success(request, 'Данные профиля успешно обновлены.')
                return redirect('profile')
            else:
                messages.error(request, 'Пожалуйста, исправьте ошибки в профиле.')
        elif 'password_submit' in request.POST:
            profile_form = ProfileForm(instance=user)
            password_form = PasswordChangeForm(user, request.POST)
            if password_form.is_valid():
                user = password_form.save()
                # чтобы сессия не упала после смены пароля
                update_session_auth_hash(request, user)
                messages.success(request, 'Пароль успешно изменён.')
                return redirect('profile')
            else:
                messages.error(request, 'Пожалуйста, исправьте ошибки при смене пароля.')
    else:
        profile_form = ProfileForm(instance=user)
        password_form = PasswordChangeForm(user)

    return render(request, 'registration/profile.html', {
        'profile_form': profile_form,
        'password_form': password_form,
    })



def base(request):
    return render(request, 'base.html')


@login_required
def delete_proposal(request, proposal_id):
    proposal = get_object_or_404(ExchangeProposal, id=proposal_id)
    # разрешаем удалять только участникам (отправителю или получателю)
    if request.user not in (proposal.ad_sender.user, proposal.ad_receiver.user):
        messages.error(request, 'У вас нет прав на удаление этого предложения.')
        return HttpResponseForbidden("Нет прав")

    if request.method == 'POST':
        proposal.delete()
        messages.success(request, 'Предложение обмена удалено.')
        return redirect('proposal_list')

    # GET — показываем страницу подтверждения
    return render(request, 'ads/confirm_delete_proposal.html', {
        'proposal': proposal
    })
