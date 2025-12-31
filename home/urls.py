from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name="index"),
    path('solicitacao/nova/', views.SolicitacaoCreateView.as_view(), name='solicitacao_nova'),
    
    # AJAX
    path('ajax/get-cnpj/', views.get_cnpj_unidade, name='ajax_get_cnpj'),
    path('ajax/get-solicitante/', views.get_dados_solicitante, name='ajax_get_solicitante'),
    
    # Aprovações
    path('pendencias/', views.ListaPendenciasView.as_view(), name='lista_pendencias'),
    path('aprovacao/<int:pk>/', views.DetalheAprovacaoView.as_view(), name='detalhe_aprovacao'),
    path('aprovacao/<int:pk>/preview/', views.VisualizarPdfView.as_view(), name='visualizar_pdf'),

    # Financeiro
    path('financeiro/notas/', views.NotaFiscalListView.as_view(), name='lista_notasfiscais'),
    path('financeiro/notas/nova/', views.NotaFiscalCreateView.as_view(), name='notafiscal_nova'),
]