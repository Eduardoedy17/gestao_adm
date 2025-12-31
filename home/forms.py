from django import forms
from .models import OrdemCompra, Unidade, NotaFiscal

class OrdemCompraForm(forms.ModelForm):
    class Meta:
        model = OrdemCompra
        fields = [
            'numero_os', 'data_os', 'solicitante', 'setor_execucao',
            'unidade', 'centro_custo', 
            'objetivo_compra', 'especialidade',
            'conta_contabil', 
            'descricao_servico', 'justificativa', 'prioridade',
            'fornecedor', 'email_fornecedor', 'condicao_pagamento',
            'valor_estimado', 'anexo_orcamento', 'tipo_contrato'
        ]
        widgets = {
            'data_os': forms.DateInput(attrs={'type': 'date'}),
            'descricao_servico': forms.Textarea(attrs={'rows': 3}),
            'justificativa': forms.Textarea(attrs={'rows': 2}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'
        
        self.fields['abreviacao_display'] = forms.CharField(label='Sigla', required=False, widget=forms.TextInput(attrs={'readonly': 'readonly', 'class': 'form-control bg-light text-center fw-bold'}))
        self.fields['cnpj_display'] = forms.CharField(label='CNPJ', required=False, widget=forms.TextInput(attrs={'readonly': 'readonly', 'class': 'form-control bg-light'}))
        self.fields['razao_social_display'] = forms.CharField(label='Razão Social', required=False, widget=forms.TextInput(attrs={'readonly': 'readonly', 'class': 'form-control bg-light text-muted'}))
        self.fields['telefone_display'] = forms.CharField(label='Telefone', required=False, widget=forms.TextInput(attrs={'readonly': 'readonly', 'class': 'form-control bg-light'}))

# --- FORMULÁRIO DE NOTA FISCAL (ATUALIZADO) ---

class NotaFiscalForm(forms.ModelForm):
    # Campos "Virtuais" do Grupo A (Para exibição/preenchimento via JS)
    os_solicitante = forms.CharField(label="Solicitante", required=False, widget=forms.TextInput(attrs={'class': 'form-control bg-light'}))
    os_unidade = forms.CharField(label="Unidade", required=False, widget=forms.TextInput(attrs={'class': 'form-control bg-light'}))
    os_setor = forms.CharField(label="Setor Destino", required=False, widget=forms.TextInput(attrs={'class': 'form-control bg-light'}))
    os_data_abertura = forms.CharField(label="Dt. Abertura Fluig", required=False, widget=forms.TextInput(attrs={'class': 'form-control bg-light'}))
    os_mes_competencia = forms.CharField(label="Mês Competência", required=False, widget=forms.TextInput(attrs={'class': 'form-control bg-light fw-bold'}))
    os_fornecedor = forms.CharField(label="Fornecedor", required=False, widget=forms.TextInput(attrs={'class': 'form-control bg-light'}))
    os_cnpj_fornecedor = forms.CharField(label="CNPJ Fornecedor", required=False, widget=forms.TextInput(attrs={'class': 'form-control bg-light'})) # Assumindo que viria da OC se tivesse
    os_especialidade = forms.CharField(label="Especialidade", required=False, widget=forms.TextInput(attrs={'class': 'form-control bg-light'}))
    os_centro_custo = forms.CharField(label="Centro de Custo", required=False, widget=forms.TextInput(attrs={'class': 'form-control bg-light'}))
    os_conta_contabil = forms.CharField(label="Conta Contábil", required=False, widget=forms.TextInput(attrs={'class': 'form-control bg-light'}))
    os_capex_opex = forms.CharField(label="CAPEX | OPEX", required=False, widget=forms.TextInput(attrs={'class': 'form-control bg-light fw-bold text-center'}))
    os_tipo_contrato = forms.CharField(label="Fixo | Spot", required=False, widget=forms.TextInput(attrs={'class': 'form-control bg-light'}))
    os_descricao = forms.CharField(label="Material/Serviço", required=False, widget=forms.Textarea(attrs={'class': 'form-control bg-light', 'rows': 2}))

    class Meta:
        model = NotaFiscal
        fields = [
            'ordem_compra', 
            # Grupo B
            'numero_nf', 'data_emissao', 'data_vencimento', 'valor_final', 'arquivo_nf',
            # Grupo C
            'tipo_lancamento', 'plaqueta'
        ]
        widgets = {
            'data_emissao': forms.DateInput(attrs={'type': 'date'}),
            'data_vencimento': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Filtro de OCs
        self.fields['ordem_compra'].queryset = OrdemCompra.objects.filter(status='APROVADO', nota_fiscal__isnull=True)
        self.fields['ordem_compra'].label = "Buscar por Ordem de Compra / Fluig"
        
        for field in self.fields.values():
            # Preserva classes existentes e adiciona form-control
            existing_class = field.widget.attrs.get('class', '')
            if 'form-control' not in existing_class:
                field.widget.attrs['class'] = existing_class + ' form-control'