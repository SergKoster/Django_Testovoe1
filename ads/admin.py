from django.contrib import admin
from .models import Ad, ExchangeProposal

@admin.register(Ad)
class AdAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'user', 'title', 'category', 'condition', 'created_at'
    )
    list_filter = (
        'category', 'condition', 'created_at',
    )
    search_fields = (
        'title', 'description', 'user__username',
    )
    raw_id_fields = ('user',)  # удобнее в больших БД
    ordering = ('-created_at',)  # новые сверху

@admin.register(ExchangeProposal)
class ExchangeProposalAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'ad_sender', 'ad_receiver', 'status', 'created_at'
    )
    list_filter = (
        'status', 'created_at',
    )
    search_fields = (
        'comment',
        'ad_sender__title',
        'ad_receiver__title',
    )
    raw_id_fields = ('ad_sender', 'ad_receiver')
    ordering = ('-created_at',)
