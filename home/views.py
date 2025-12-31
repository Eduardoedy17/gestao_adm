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

# ... (Views existentes: index, SolicitacaoCreateView, get_cnpj_unidade, get_dados_solicitante, ListaPendenciasView, DetalheAprovacaoView, VisualizarPdfView mantidas) ...

# 1. Dashboard
def index(request):
    return render(request, 'index.html')

class SolicitacaoCreateView(CreateView):
    model = OrdemCompra
    form_class = OrdemCompraForm
    template_name = 'home/form_solicitacao.html'
    success_url = reverse_lazy('index')
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo_conteudo'] = "Nova Solicitação de Compra/Serviço"
        return context

def get_cnpj_unidade(request):
    unidade_id = request.GET.get('unidade_id')
    try:
        unidade = Unidade.objects.get(id=unidade_id)
        data = {'cnpj': unidade.cnpj, 'abreviacao': unidade.abreviacao, 'razao_social': unidade.razao_social}
    except (Unidade.DoesNotExist, ValueError):
        data = {'cnpj': '', 'abreviacao': '', 'razao_social': ''}
    return JsonResponse(data)

def get_dados_solicitante(request):
    solicitante_id = request.GET.get('solicitante_id')
    try:
        solicitante = Solicitante.objects.get(id=solicitante_id)
        data = {'telefone': solicitante.telefone if solicitante.telefone else 'Não cadastrado'}
    except (Solicitante.DoesNotExist, ValueError):
        data = {'telefone': ''}
    return JsonResponse(data)

class ListaPendenciasView(ListView):
    model = OrdemCompra
    template_name = 'home/lista_pendencias.html'
    context_object_name = 'solicitacoes'
    def get_queryset(self):
        return OrdemCompra.objects.select_related('unidade', 'solicitante').filter(status='SOLICITADO').order_by('-data_criacao')

class DetalheAprovacaoView(DetailView):
    model = OrdemCompra
    template_name = 'home/detalhe_aprovacao.html'
    context_object_name = 'oc'
    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        acao = request.POST.get('acao')
        motivo = request.POST.get('motivo_reprovacao')
        if self.object.status != 'SOLICITADO':
            messages.error(request, 'Processado anteriormente.')
            return redirect('lista_pendencias')
        if acao == 'aprovar':
            self.object.status = 'APROVADO'
            self.object.aprovado_por = request.user
            self.object.data_aprovacao = timezone.now()
            self.object.save()
            pdf, fname = gerar_pdf_ordem_compra(self.object)
            if pdf:
                response = HttpResponse(pdf, content_type='application/pdf')
                response['Content-Disposition'] = f'attachment; filename="{fname}"'
                return response
            return redirect('lista_pendencias')
        elif acao == 'reprovar':
            self.object.status = 'REPROVADO'
            self.object.motivo_reprovacao = motivo
            self.object.save()
            return redirect('lista_pendencias')
        return redirect('lista_pendencias')

class VisualizarPdfView(DetailView):
    model = OrdemCompra
    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        pdf, fname = gerar_pdf_ordem_compra(self.object)
        if pdf:
            response = HttpResponse(pdf, content_type='application/pdf')
            response['Content-Disposition'] = f'inline; filename="{fname}"'
            return response
        return HttpResponse("Erro PDF")

# --- MÓDULO FINANCEIRO ---

class NotaFiscalListView(ListView):
    model = NotaFiscal
    template_name = 'home/lista_notasfiscais.html'
    context_object_name = 'notas'
    ordering = ['-data_lancamento']

# NOVA VIEW AJAX: Busca detalhes da OC para o formulário de NF
def get_detalhes_ordem_compra(request):
    oc_id = request.GET.get('oc_id')
    try:
        oc = OrdemCompra.objects.get(id=oc_id)
        
        # Lógica do Mês (Month(Data OS))
        meses = ['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho', 
                 'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro']
        mes_competencia = meses[oc.data_os.month - 1]

        data = {
            'success': True,
            'solicitante': oc.solicitante.nome,
            'unidade': oc.unidade.nome,
            'setor': oc.setor_execucao,
            'data_abertura': oc.data_os.strftime('%Y-%m-%d'), # Formato ISO para inputs de data
            'mes_competencia': mes_competencia,
            'fornecedor': oc.fornecedor,
            'cnpj': oc.unidade.cnpj, # Na falta de CNPJ do fornecedor na OC, enviamos da Unidade ou Vazio
            'especialidade': oc.get_especialidade_display(),
            'centro_custo': str(oc.centro_custo),
            'conta_contabil': oc.get_conta_contabil_display(),
            'capex_opex': oc.classificacao,
            'tipo_contrato': oc.get_tipo_contrato_display(),
            'descricao': oc.descricao_servico,
            'valor_estimado': str(oc.valor_estimado)
        }
    except OrdemCompra.DoesNotExist:
        data = {'success': False}
    
    return JsonResponse(data)


class NotaFiscalCreateView(CreateView):
    model = NotaFiscal
    form_class = NotaFiscalForm
    template_name = 'home/form_notafiscal.html'
    success_url = reverse_lazy('lista_notasfiscais')

    def form_valid(self, form):
        if self.request.user.is_authenticated:
            form.instance.responsavel_lancamento = self.request.user
        messages.success(self.request, "Nota Fiscal lançada com sucesso!")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo_conteudo'] = "Lançamento de Nota Fiscal"
        return context