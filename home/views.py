from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import CreateView, TemplateView, ListView, UpdateView
from django.urls import reverse_lazy
from django.http import JsonResponse
from django.contrib.auth.mixins import LoginRequiredMixin # Para exigir login depois
from .models import OrdemCompra, Unidade
from .forms import OrdemCompraForm

# 1. Dashboard (Sua página inicial)
def index(request):
    # Aqui depois colocaremos os contadores reais
    return render(request, 'index.html')

# 2. View de Solicitação (O Formulário)
class SolicitacaoCreateView(CreateView):
    model = OrdemCompra
    form_class = OrdemCompraForm
    template_name = 'home/form_solicitacao.html'
    success_url = reverse_lazy('index') # Volta para home ao salvar

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo_conteudo'] = "Nova Solicitação de Compra/Serviço"
        return context

# 3. View Auxiliar (AJAX) - Retorna o CNPJ quando escolhe a Unidade
def get_cnpj_unidade(request):
    unidade_id = request.GET.get('unidade_id')
    try:
        unidade = Unidade.objects.get(id=unidade_id)
        data = {'cnpj': unidade.cnpj}
    except (Unidade.DoesNotExist, ValueError):
        data = {'cnpj': ''}
    return JsonResponse(data)