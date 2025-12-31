from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import CreateView, ListView, DetailView
from django.urls import reverse_lazy
from django.http import JsonResponse, HttpResponse
from django.contrib import messages
from django.utils import timezone
from django.contrib.auth.mixins import LoginRequiredMixin

from .models import OrdemCompra, Unidade, Solicitante, NotaFiscal
from .forms import OrdemCompraForm, NotaFiscalForm
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

# 3. AJAX Dados Unidade (CNPJ + Abreviação + Razão Social)
def get_cnpj_unidade(request):
    unidade_id = request.GET.get('unidade_id')
    try:
        unidade = Unidade.objects.get(id=unidade_id)
        data = {
            'cnpj': unidade.cnpj,
            'abreviacao': unidade.abreviacao,
            'razao_social': unidade.razao_social
        }
    except (Unidade.DoesNotExist, ValueError):
        data = {'cnpj': '', 'abreviacao': '', 'razao_social': ''}
    return JsonResponse(data)

# 4. AJAX Telefone (Solicitante)
def get_dados_solicitante(request):
    solicitante_id = request.GET.get('solicitante_id')
    try:
        solicitante = Solicitante.objects.get(id=solicitante_id)
        data = {'telefone': solicitante.telefone if solicitante.telefone else 'Não cadastrado'}
    except (Solicitante.DoesNotExist, ValueError):
        data = {'telefone': ''}
    return JsonResponse(data)

# 5. Lista de Pendências
class ListaPendenciasView(ListView):
    model = OrdemCompra
    template_name = 'home/lista_pendencias.html'
    context_object_name = 'solicitacoes'

    def get_queryset(self):
        return OrdemCompra.objects.select_related('unidade', 'solicitante').filter(status='SOLICITADO').order_by('-data_criacao')

# 6. Detalhe e Aprovação
class DetalheAprovacaoView(DetailView):
    model = OrdemCompra
    template_name = 'home/detalhe_aprovacao.html'
    context_object_name = 'oc'

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        acao = request.POST.get('acao')
        motivo = request.POST.get('motivo_reprovacao')

        if self.object.status != 'SOLICITADO':
            messages.error(request, 'Esta solicitação já foi processada.')
            return redirect('lista_pendencias')

        if acao == 'aprovar':
            self.object.status = 'APROVADO'
            self.object.aprovado_por = request.user if request.user.is_authenticated else None
            self.object.data_aprovacao = timezone.now()
            self.object.save()
            
            pdf_content, filename = gerar_pdf_ordem_compra(self.object)
            
            if pdf_content:
                response = HttpResponse(pdf_content, content_type='application/pdf')
                response['Content-Disposition'] = f'attachment; filename="{filename}"'
                return response
            else:
                messages.warning(request, "Ordem aprovada com sucesso! (PDF indisponível neste ambiente serverless).")
                return redirect('lista_pendencias')

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

# 7. Pré-visualização do PDF
class VisualizarPdfView(DetailView):
    model = OrdemCompra
    
    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        
        pdf_content, filename = gerar_pdf_ordem_compra(self.object)
        
        if pdf_content:
            response = HttpResponse(pdf_content, content_type='application/pdf')
            response['Content-Disposition'] = f'inline; filename="PREVIA_{filename}"'
            return response
        else:
            return HttpResponse("<h1>Visualização indisponível</h1><p>O ambiente Vercel não suporta as bibliotecas gráficas necessárias para gerar o PDF.</p>", status=503)

# 8. Lista de Notas Fiscais (FINANCEIRO)
class NotaFiscalListView(ListView):
    model = NotaFiscal
    template_name = 'home/lista_notasfiscais.html'
    context_object_name = 'notas'
    ordering = ['-data_lancamento']

# 9. Lançamento de Nova NF (FINANCEIRO)
class NotaFiscalCreateView(CreateView):
    model = NotaFiscal
    form_class = NotaFiscalForm
    template_name = 'home/form_notafiscal.html'
    success_url = reverse_lazy('lista_notasfiscais')

    def form_valid(self, form):
        if self.request.user.is_authenticated:
            form.instance.responsavel_lancamento = self.request.user
        messages.success(self.request, "Nota Fiscal lançada com sucesso! A Ordem de Compra foi concluída.")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo_conteudo'] = "Lançamento de Nota Fiscal"
        return context