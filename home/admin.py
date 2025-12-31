from django.contrib import admin
from .models import Unidade, CentroCusto, Solicitante, OrdemCompra, NotaFiscal

@admin.register(OrdemCompra)
class OrdemCompraAdmin(admin.ModelAdmin):
    list_display = ('id', 'numero_os', 'unidade', 'fornecedor', 'valor_estimado', 'status', 'prioridade')
    list_filter = ('status', 'prioridade', 'classificacao', 'unidade')
    search_fields = ('numero_os', 'fornecedor', 'descricao_servico')
    readonly_fields = ('data_criacao', 'data_atualizacao', 'data_aprovacao', 'aprovado_por')
    
    fieldsets = (
        ('Identificação', {
            'fields': ('numero_os', 'data_os', 'solicitante', 'setor_execucao', 'unidade', 'centro_custo')
        }),
        ('Classificação', {
            'fields': ('objetivo_compra', 'especialidade', 'conta_contabil', 'classificacao')
        }),
        ('Detalhes da Compra', {
            'fields': ('descricao_servico', 'justificativa', 'prioridade', 'anexo_orcamento')
        }),
        ('Fornecedor e Valores', {
            'fields': ('fornecedor', 'email_fornecedor', 'condicao_pagamento', 'valor_estimado')
        }),
        ('Controle Interno', {
            'fields': ('status', 'data_criacao', 'aprovado_por', 'data_aprovacao', 'motivo_reprovacao')
        }),
    )

@admin.register(Solicitante)
class SolicitanteAdmin(admin.ModelAdmin):
    list_display = ('nome', 'email', 'telefone', 'cargo')
    search_fields = ('nome', 'email')

@admin.register(Unidade)
class UnidadeAdmin(admin.ModelAdmin):
    list_display = ('abreviacao', 'nome', 'cnpj')
    search_fields = ('nome', 'abreviacao', 'cnpj')

@admin.register(NotaFiscal)
class NotaFiscalAdmin(admin.ModelAdmin):
    list_display = ('numero_nf', 'ordem_compra', 'data_emissao', 'valor_total')
    search_fields = ('numero_nf', 'numero_fluig')

    def valor_total(self, obj):
        return obj.ordem_compra.valor_estimado
    valor_total.short_description = 'Valor (OC)'

# Registros simples
admin.site.register(CentroCusto)