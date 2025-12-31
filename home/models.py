from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import os

# --- Entidades de Base (Cadastros Gerais) ---

class Unidade(models.Model):
    """
    Representa as unidades do Grupo Med Imagem e seus CNPJs.
    """
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
    """
    O coração do sistema. Gerencia o fluxo da solicitação.
    Agora expandido para incluir dados de OS e Classificações detalhadas.
    """
    
    # --- LISTAS DE OPÇÕES (CHOICES) ---
    
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
        # OPEX
        ('AGUA_ESGOTO', 'Água e Esgoto (OPEX)'),
        ('ENERGIA', 'Energia Elétrica (OPEX)'),
        ('GASES_MED', 'Gases Medicinais (OPEX)'),
        ('ALUGUEL_EQUIP', 'Aluguel de Equipamentos (OPEX)'),
        ('MANUT_PREDIAL', 'Manutenção Predial (OPEX)'),
        ('MANUT_EQUIP', 'Manutenção de Equipamentos (OPEX)'),
        ('MANUT_MOVEIS', 'Manutenção de Móveis e Utensílios (OPEX)'),
        # CAPEX / OUTROS
        ('INVESTIMENTO', 'Investimento / CAPEX (Outros)'),
    ]

    PRIORIDADE_CHOICES = [
        ('BAIXA', 'Baixa'),
        ('MEDIA', 'Média'),
        ('ALTA', 'Alta'),
        ('URGENTE', 'Urgente'),
    ]

    # --- A. DADOS DE IDENTIFICAÇÃO (CABEÇALHO) ---
    numero_os = models.CharField(max_length=50, verbose_name="Número da OS", help_text="ID único da Ordem de Serviço")
    data_os = models.DateField(verbose_name="Data da OS")
    solicitante = models.ForeignKey(Solicitante, on_delete=models.PROTECT, related_name='ordens', verbose_name="Solicitante Responsável")
    setor_execucao = models.CharField(max_length=100, verbose_name="Setor de Execução", help_text="Local onde o serviço/material será aplicado")
    unidade = models.ForeignKey(Unidade, on_delete=models.PROTECT)
    centro_custo = models.ForeignKey(CentroCusto, on_delete=models.PROTECT)

    # --- B. CLASSIFICAÇÃO DO PEDIDO ---
    objetivo_compra = models.CharField(max_length=30, choices=OBJETIVO_COMPRA_CHOICES, verbose_name="Objetivo da Compra")
    especialidade = models.CharField(max_length=30, choices=ESPECIALIDADE_CHOICES, verbose_name="Especialidade")

    # --- C. CLASSIFICAÇÃO CONTÁBIL ---
    conta_contabil = models.CharField(max_length=30, choices=CONTA_CONTABIL_CHOICES, verbose_name="Conta Contábil")
    classificacao = models.CharField(max_length=10, choices=TIPO_CLASSIFICACAO, verbose_name="Classificação Geral (CAPEX/OPEX)")

    # --- D. DETALHES E FORNECEDOR ---
    descricao_servico = models.TextField(verbose_name="Descrição do Material/Serviço")
    justificativa = models.TextField(verbose_name="Justificativa da Compra")
    prioridade = models.CharField(max_length=10, choices=PRIORIDADE_CHOICES, default='MEDIA', verbose_name="Grau de Prioridade")
    
    # Dados Financeiros/Fornecedor
    fornecedor = models.CharField(max_length=150, verbose_name="Nome do Fornecedor")
    email_fornecedor = models.EmailField(verbose_name="E-mail do Fornecedor", blank=True, null=True)
    condicao_pagamento = models.CharField(max_length=100, verbose_name="Condições de Pagamento", help_text="Ex: Boleto 30 dias, À vista, Pix")
    valor_estimado = models.DecimalField(max_digits=12, decimal_places=2)
    anexo_orcamento = models.FileField(upload_to='orcamentos/%Y/%m/', verbose_name="Orçamento (PDF)")

    # --- CONTROLE ---
    data_criacao = models.DateTimeField(auto_now_add=True)
    data_atualizacao = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=20, choices=STATUS_PEDIDO, default='RASCUNHO')
    
    data_aprovacao = models.DateTimeField(null=True, blank=True)
    aprovado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='aprovacoes')
    motivo_reprovacao = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"OS {self.numero_os} - {self.fornecedor}"

    def save(self, *args, **kwargs):
        # Regra de Negócio: Validação Automática de CAPEX/OPEX baseada na Conta Contábil
        contas_opex = [
            'AGUA_ESGOTO', 'ENERGIA', 'GASES_MED', 'ALUGUEL_EQUIP',
            'MANUT_PREDIAL', 'MANUT_EQUIP', 'MANUT_MOVEIS'
        ]
        
        if self.conta_contabil in contas_opex:
            self.classificacao = 'OPEX'
        else:
            self.classificacao = 'CAPEX'
            
        super().save(*args, **kwargs)

# --- Módulo Financeiro ---
class NotaFiscal(models.Model):
    ordem_compra = models.OneToOneField(OrdemCompra, on_delete=models.CASCADE, related_name='nota_fiscal')
    numero_nf = models.CharField(max_length=50, verbose_name="Número da NF")
    numero_fluig = models.CharField(max_length=50, verbose_name="Número Fluig", help_text="ID do processo no Fluig")
    data_emissao = models.DateField()
    arquivo_nf = models.FileField(upload_to='notas_fiscais/%Y/%m/')
    data_lancamento = models.DateTimeField(auto_now_add=True)
    responsavel_lancamento = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f"NF {self.numero_nf} ref. OC #{self.ordem_compra.pk}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.ordem_compra.status != 'CONCLUIDO':
            self.ordem_compra.status = 'CONCLUIDO'
            self.ordem_compra.save()