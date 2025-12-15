from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name="index"),
    path('solicitacao/nova/', views.SolicitacaoCreateView.as_view(), name='solicitacao_nova'),
    path('ajax/get-cnpj/', views.get_cnpj_unidade, name='ajax_get_cnpj'),
    path('pendencias/', views.ListaPendenciasView.as_view(), name='lista_pendencias'),
    path('aprovacao/<int:pk>/', views.DetalheAprovacaoView.as_view(), name='detalhe_aprovacao'),
    
    # Rota nova que faltava
    path('aprovacao/<int:pk>/preview/', views.VisualizarPdfView.as_view(), name='visualizar_pdf'),
]