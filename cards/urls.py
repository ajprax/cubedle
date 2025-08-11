from django.urls import path
from . import views

app_name = 'cards'

urlpatterns = [
    path('', views.landing_page, name='landing'),
    path('head-to-head/', views.head_to_head, name='head_to_head'),
    path('vote/', views.vote, name='vote'),
    path('suggest/', views.suggest_card, name='suggest'),
    path('search-card/', views.search_card, name='search_card'),
    path('add-card/', views.add_card, name='add_card'),
    path('bulk-add-cards/', views.bulk_add_cards, name='bulk_add_cards'),
    path('standings/', views.standings, name='standings'),
    path('diagnostics/', views.diagnostics, name='diagnostics'),
    path('update-card/', views.update_card, name='update_card'),
    path('delete-card/', views.delete_card, name='delete_card'),
]