from django import forms
from .models import OrdemCompra, Unidade, NotaFiscal

class OrdemCompraForm(forms.ModelForm):
    class Meta:
        model = OrdemCompra
        fields = [
            # A. Identificação
            'numero_os', 'data_os', 'solicitante', 'setor_execucao',
            'unidade', 'centro_custo', 
            # B. Classificação
            'objetivo_compra', 'especialidade',
            # C. Contábil
            'conta_contabil', # 'classificacao' é automático
            # D. Detalhes
            'descricao_servico', 'justificativa', 'prioridade',
            'fornecedor', 'email_fornecedor', 'condicao_pagamento',
            'valor_estimado', 'anexo_orcamento'
        ]
        widgets = {
            'data_os': forms.DateInput(attrs={'type': 'date'}),
            'descricao_servico': forms.Textarea(attrs={'rows': 3}),
            'justificativa': forms.Textarea(attrs={'rows': 2}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Adiciona classes CSS Bootstrap em todos os campos
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'
        
        # Campos de Visualização (Readonly)
        self.fields['abreviacao_display'] = forms.CharField(
            label='Sigla', required=False, widget=forms.TextInput(attrs={'readonly': 'readonly', 'class': 'form-control bg-light text-center fw-bold'})
        )
        self.fields['cnpj_display'] = forms.CharField(
            label='CNPJ', required=False, widget=forms.TextInput(attrs={'readonly': 'readonly', 'class': 'form-control bg-light'})
        )
        self.fields['razao_social_display'] = forms.CharField(
            label='Razão Social', required=False, widget=forms.TextInput(attrs={'readonly': 'readonly', 'class': 'form-control bg-light text-muted'})
        )
        self.fields['telefone_display'] = forms.CharField(
            label='Telefone', required=False, widget=forms.TextInput(attrs={'readonly': 'readonly', 'class': 'form-control bg-light'})
        )

class NotaFiscalForm(forms.ModelForm):
    class Meta:
        model = NotaFiscal
        fields = ['ordem_compra', 'numero_nf', 'numero_fluig', 'data_emissao', 'arquivo_nf']
        widgets = {
            'data_emissao': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['ordem_compra'].queryset = OrdemCompra.objects.filter(status='APROVADO', nota_fiscal__isnull=True)
        self.fields['ordem_compra'].label = "Selecione a Ordem de Compra (Aprovada)"
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'