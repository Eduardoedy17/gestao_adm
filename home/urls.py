from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name="index"),
    
    # Nova rota para o formulário
    path('solicitacao/nova/', views.SolicitacaoCreateView.as_view(), name='solicitacao_nova'),
    
    # Rota para o AJAX buscar o CNPJ (Front-end chama essa URL)
    path('ajax/get-cnpj/', views.get_cnpj_unidade, name='ajax_get_cnpj'),

    # Rota para a lista de pendências
    path('pendencias/', views.ListaPendenciasView.as_view(), name='lista_pendencias'),
    
    # Rota para o detalhe da aprovação
    path('aprovacao/<int:pk>/', views.DetalheAprovacaoView.as_view(), name='detalhe_aprovacao'),

    # Rota para visualizar o PDF da ordem de compra
    path('aprovacao/<int:pk>/preview/', views.VisualizarPdfView.as_view(), name='visualizar_pdf'),
]