from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import CreateView, ListView, DetailView
from django.urls import reverse_lazy
from django.http import JsonResponse, HttpResponse
from django.contrib import messages
from django.utils import timezone
from django.contrib.auth.mixins import LoginRequiredMixin

from .models import OrdemCompra, Unidade
from .forms import OrdemCompraForm
from .utils import gerar_pdf_ordem_compra

# 1. Dashboard
def index(request):
    return render(request, 'index.html')

# 2. Nova Solicitação
class SolicitacaoCreateView(CreateView):
    model = OrdemCompra
    form_class = OrdemCompraForm
    template_name = 'home/form_solicitacao.html'
    success_url = reverse_lazy('index')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo_conteudo'] = "Nova Solicitação de Compra/Serviço"
        return context

# 3. AJAX CNPJ
def get_cnpj_unidade(request):
    unidade_id = request.GET.get('unidade_id')
    try:
        unidade = Unidade.objects.get(id=unidade_id)
        data = {'cnpj': unidade.cnpj}
    except (Unidade.DoesNotExist, ValueError):
        data = {'cnpj': ''}
    return JsonResponse(data)

# 4. Lista de Pendências (Com otimização de consulta)
class ListaPendenciasView(ListView):
    model = OrdemCompra
    template_name = 'home/lista_pendencias.html'
    context_object_name = 'solicitacoes'

    def get_queryset(self):
        # select_related melhora a performance buscando Unidade e Solicitante juntos
        return OrdemCompra.objects.select_related('unidade', 'solicitante').filter(status='SOLICITADO').order_by('-data_criacao')

# 5. Detalhe e Aprovação
class DetalheAprovacaoView(DetailView):
    model = OrdemCompra
    template_name = 'home/detalhe_aprovacao.html'
    context_object_name = 'oc'

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        acao = request.POST.get('acao')
        motivo = request.POST.get('motivo_reprovacao')

        # Segurança: impede alteração se não estiver pendente
        if self.object.status != 'SOLICITADO':
            messages.error(request, 'Esta solicitação já foi processada.')
            return redirect('lista_pendencias')

        if acao == 'aprovar':
            # Atualiza status
            self.object.status = 'APROVADO'
            self.object.aprovado_por = request.user if request.user.is_authenticated else None
            self.object.data_aprovacao = timezone.now()
            self.object.save()
            
            # Gera PDF
            pdf_content, filename = gerar_pdf_ordem_compra(self.object)
            
            # Retorna download
            response = HttpResponse(pdf_content, content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            return response

        elif acao == 'reprovar':
            if not motivo:
                messages.error(request, 'É obrigatório informar o motivo da reprovação.')
                return redirect('detalhe_aprovacao', pk=self.object.pk)
            
            self.object.status = 'REPROVADO'
            self.object.motivo_reprovacao = motivo
            self.object.aprovado_por = request.user if request.user.is_authenticated else None
            self.object.data_aprovacao = timezone.now()
            self.object.save()
            messages.success(request, 'Solicitação reprovada com sucesso.')
            return redirect('lista_pendencias')

        return redirect('lista_pendencias')

# 6. Pré-visualização do PDF (NOVO - FALTAVA ISTO)
class VisualizarPdfView(DetailView):
    model = OrdemCompra
    
    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        # Gera o PDF mas define para abrir no navegador (inline)
        pdf_content, filename = gerar_pdf_ordem_compra(self.object)
        response = HttpResponse(pdf_content, content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename="PREVIA_{filename}"'
        return response