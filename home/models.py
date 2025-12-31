from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import os

# ... (Unidade, CentroCusto, Solicitante mantidos iguais) ...

class Unidade(models.Model):
    abreviacao = models.CharField(max_length=20, verbose_name="Sigla / Abreviação", help_text="Ex: HMI, PMA")
    nome = models.CharField(max_length=100, verbose_name="Nome da Unidade", help_text="Ex: Hospital Med Imagem")
    razao_social = models.CharField(max_length=150, verbose_name="Razão Social")
    cnpj = models.CharField(max_length=20, verbose_name="CNPJ", help_text="Formato: 00.000.000/0000-00")

    class Meta:
        verbose_name = "Unidade"
        verbose_name_plural = "Unidades"
        ordering = ['abreviacao']

    def __str__(self):
        return self.nome

class CentroCusto(models.Model):
    codigo = models.CharField(max_length=20, unique=True)
    descricao = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.codigo} - {self.descricao}"

class Solicitante(models.Model):
    nome = models.CharField(max_length=100)
    cargo = models.CharField(max_length=100, blank=True, null=True)
    email = models.EmailField()
    telefone = models.CharField(max_length=20, blank=True, null=True, verbose_name="Telefone / WhatsApp")
    usuario_sistema = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.nome

# --- Entidade Principal (Solicitação) ---

class OrdemCompra(models.Model):
    # Choices existentes...
    TIPO_CLASSIFICACAO = [
        ('CAPEX', 'CAPEX (Investimento/Obras/Bens)'),
        ('OPEX', 'OPEX (Custeio/Manutenção/Materiais)'),
    ]
    STATUS_PEDIDO = [
        ('RASCUNHO', 'Rascunho'),
        ('SOLICITADO', 'Aguardando Aprovação'),
        ('APROVADO', 'Aprovado (Ordem Gerada)'),
        ('REPROVADO', 'Reprovado'),
        ('CONCLUIDO', 'Concluído (NF Lançada)'),
    ]
    OBJETIVO_COMPRA_CHOICES = [
        ('IMOBILIZADO', 'Aquisição de Bens Imobilizados'),
        ('MATERIAL', 'Compra de Material (Direto/Indireto)'),
        ('OBRAS', 'Obras'),
        ('REFORMA_OPEX', 'Reforma (OPEX)'),
        ('REFORMA_CAPEX', 'Reforma (CAPEX)'),
        ('MANUT_PREVENTIVA', 'Manutenção Preventiva'),
        ('MANUT_CORRETIVA', 'Manutenção Corretiva'),
    ]
    ESPECIALIDADE_CHOICES = [
        ('ELETRICA', 'Elétrica'),
        ('HIDRAULICA', 'Hidráulica'),
        ('ENG_CLINICA', 'Engenharia Clínica'),
        ('OBRAS_CIVIL', 'Obras / Civil'),
        ('OPERACIONAL', 'Operacional'),
        ('REFRIGERACAO', 'Refrigeração'),
        ('GASES', 'Gases Medicinais / Rede de Gases'),
        ('UTILITIES', 'Utilities (Energia/Água/Esgoto)'),
    ]
    CONTA_CONTABIL_CHOICES = [
        ('AGUA_ESGOTO', 'Água e Esgoto (OPEX)'),
        ('ENERGIA', 'Energia Elétrica (OPEX)'),
        ('GASES_MED', 'Gases Medicinais (OPEX)'),
        ('ALUGUEL_EQUIP', 'Aluguel de Equipamentos (OPEX)'),
        ('MANUT_PREDIAL', 'Manutenção Predial (OPEX)'),
        ('MANUT_EQUIP', 'Manutenção de Equipamentos (OPEX)'),
        ('MANUT_MOVEIS', 'Manutenção de Móveis e Utensílios (OPEX)'),
        ('INVESTIMENTO', 'Investimento / CAPEX (Outros)'),
    ]
    PRIORIDADE_CHOICES = [
        ('BAIXA', 'Baixa'),
        ('MEDIA', 'Média'),
        ('ALTA', 'Alta'),
        ('URGENTE', 'Urgente'),
    ]
    # NOVO CHOICE
    TIPO_CONTRATO_CHOICES = [
        ('FIXO', 'Fixo / Recorrente'),
        ('SPOT', 'Spot / Pontual'),
    ]

    # Campos
    numero_os = models.CharField(max_length=50, verbose_name="Número da OS")
    data_os = models.DateField(verbose_name="Data da OS")
    solicitante = models.ForeignKey(Solicitante, on_delete=models.PROTECT, related_name='ordens')
    setor_execucao = models.CharField(max_length=100, verbose_name="Setor de Execução")
    unidade = models.ForeignKey(Unidade, on_delete=models.PROTECT)
    centro_custo = models.ForeignKey(CentroCusto, on_delete=models.PROTECT)

    objetivo_compra = models.CharField(max_length=30, choices=OBJETIVO_COMPRA_CHOICES)
    especialidade = models.CharField(max_length=30, choices=ESPECIALIDADE_CHOICES)
    conta_contabil = models.CharField(max_length=30, choices=CONTA_CONTABIL_CHOICES)
    classificacao = models.CharField(max_length=10, choices=TIPO_CLASSIFICACAO)
    
    # NOVO CAMPO DE CONTRATO
    tipo_contrato = models.CharField(max_length=10, choices=TIPO_CONTRATO_CHOICES, default='SPOT', verbose_name="Tipo de Contrato")

    descricao_servico = models.TextField()
    justificativa = models.TextField()
    prioridade = models.CharField(max_length=10, choices=PRIORIDADE_CHOICES, default='MEDIA')
    
    fornecedor = models.CharField(max_length=150)
    email_fornecedor = models.EmailField(blank=True, null=True)
    condicao_pagamento = models.CharField(max_length=100)
    valor_estimado = models.DecimalField(max_digits=12, decimal_places=2)
    anexo_orcamento = models.FileField(upload_to='orcamentos/%Y/%m/')

    data_criacao = models.DateTimeField(auto_now_add=True)
    data_atualizacao = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=20, choices=STATUS_PEDIDO, default='RASCUNHO')
    data_aprovacao = models.DateTimeField(null=True, blank=True)
    aprovado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='aprovacoes')
    motivo_reprovacao = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"OS {self.numero_os} - {self.fornecedor}"

    def save(self, *args, **kwargs):
        contas_opex = ['AGUA_ESGOTO', 'ENERGIA', 'GASES_MED', 'ALUGUEL_EQUIP', 'MANUT_PREDIAL', 'MANUT_EQUIP', 'MANUT_MOVEIS']
        if self.conta_contabil in contas_opex:
            self.classificacao = 'OPEX'
        else:
            self.classificacao = 'CAPEX'
        super().save(*args, **kwargs)

# --- Módulo Financeiro ---

class NotaFiscal(models.Model):
    TIPO_LANCAMENTO_CHOICES = [
        ('FLUIG', 'Com Pedido Fluig'),
        ('REGULARIZACAO', 'Regularização'),
        ('MEDICAO', 'Medição de Contrato'),
        ('DIVERSOS', 'Pagamentos Diversos'),
    ]

    ordem_compra = models.OneToOneField(OrdemCompra, on_delete=models.CASCADE, related_name='nota_fiscal', verbose_name="Ordem de Compra / Fluig")
    
    # Grupo B: Dados da NF
    numero_nf = models.CharField(max_length=50, verbose_name="Número da NF")
    numero_fluig = models.CharField(max_length=50, verbose_name="Número Fluig (Legado)", blank=True, null=True) # Tornado opcional pois o vínculo é pela OC
    data_emissao = models.DateField(verbose_name="Data de Emissão")
    data_vencimento = models.DateField(verbose_name="Data de Vencimento", null=True, blank=True) # Novo
    valor_final = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Valor Final da Nota", null=True) # Novo (editável)
    
    # Grupo C: Lógica Condicional
    tipo_lancamento = models.CharField(max_length=20, choices=TIPO_LANCAMENTO_CHOICES, default='FLUIG', verbose_name="Tipo de Lançamento")
    plaqueta = models.CharField(max_length=50, blank=True, null=True, verbose_name="Plaqueta (Ativo Imobilizado)", help_text="Obrigatório se for CAPEX")

    arquivo_nf = models.FileField(upload_to='notas_fiscais/%Y/%m/')
    data_lancamento = models.DateTimeField(auto_now_add=True)
    responsavel_lancamento = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f"NF {self.numero_nf}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.ordem_compra.status != 'CONCLUIDO':
            self.ordem_compra.status = 'CONCLUIDO'
            self.ordem_compra.save()