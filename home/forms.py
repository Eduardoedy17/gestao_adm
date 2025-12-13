from django import forms
from .models import OrdemCompra, Unidade

class OrdemCompraForm(forms.ModelForm):
    class Meta:
        model = OrdemCompra
        fields = [
            'unidade', 'centro_custo', 'solicitante', 
            'classificacao', 'descricao_servico', 
            'fornecedor', 'valor_estimado', 'anexo_orcamento'
        ]
        widgets = {
            'descricao_servico': forms.Textarea(attrs={'rows': 3}),
            'data_entrega': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Adiciona classes CSS do Bootstrap para ficar bonito
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'
        
        # O campo CNPJ não existe no model OrdemCompra, mas queremos exibi-lo no form
        # como apenas leitura para feedback visual.
        self.fields['cnpj_display'] = forms.CharField(
            label='CNPJ da Unidade', 
            required=False, 
            widget=forms.TextInput(attrs={'readonly': 'readonly', 'class': 'form-control'})
        )