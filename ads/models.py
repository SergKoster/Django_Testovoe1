from django.db import models
from django.contrib.auth.models import User  # Стандартная модель пользователя Django


class Ad(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ads')
    title = models.CharField(max_length=255)
    description = models.TextField()
    image = models.ImageField(
        upload_to='ads_images/',  # папка внутри MEDIA_ROOT
        blank=True,
        null=True
    )
    category = models.CharField(max_length=100)
    condition = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} ({self.user.username})"
    # __str__ — строковое представление объекта, удобно для отображения в админке и shell.


class ExchangeProposal(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Ожидает'),
        ('accepted', 'Принята'),
        ('rejected', 'Отклонена'),
    ]

    ad_sender = models.ForeignKey(Ad, on_delete=models.CASCADE, related_name='sent_proposals')
    ad_receiver = models.ForeignKey(Ad, on_delete=models.CASCADE, related_name='received_proposals')
    comment = models.TextField(blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Proposal from Ad {self.ad_sender_id} to Ad {self.ad_receiver_id} ({self.get_status_display()})"
    # __str__ — строковое отображение, get_status_display() возвращает человекочитаемый статус ("Ожидает" и т.д.).
