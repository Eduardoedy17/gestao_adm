from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import os

# --- Entidades de Base (Cadastros Gerais) ---

class Unidade(models.Model):
    """
    Representa as unidades do Grupo Med Imagem e seus CNPJs.
    Refatorado para ser dinâmico: permite cadastrar novas unidades pelo Admin.
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
        return f"{self.abreviacao} - {self.nome}"

class CentroCusto(models.Model):
    """
    Centros de Custo para alocação financeira.
    """
    codigo = models.CharField(max_length=20, unique=True)
    descricao = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.codigo} - {self.descricao}"

class Solicitante(models.Model):
    """
    Cadastro de solicitantes autorizados.
    Pode ser vinculado ao User do Django posteriormente para login.
    """
    nome = models.CharField(max_length=100)
    cargo = models.CharField(max_length=100, blank=True, null=True)
    email = models.EmailField()
    usuario_sistema = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.nome

# --- Entidade Principal (Solicitação) ---

class OrdemCompra(models.Model):
    """
    O coração do sistema. Gerencia o fluxo da solicitação.
    """
    # Choices conforme especificação (Mantidos fixos para lógica de negócio)
    TIPO_CLASSIFICACAO = [
        ('CAPEX', 'CAPEX (Investimento/Obras/Bens)'),
        ('OPEX', 'OPEX (Custeio/Manutenção/Materiais)'),
    ]

    # Máquina de Estados (State Machine)
    STATUS_PEDIDO = [
        ('RASCUNHO', 'Rascunho'),
        ('SOLICITADO', 'Aguardando Aprovação'),
        ('APROVADO', 'Aprovado (Ordem Gerada)'),
        ('REPROVADO', 'Reprovado'),
        ('CONCLUIDO', 'Concluído (NF Lançada)'),
    ]

    # Dados da Solicitação
    solicitante = models.ForeignKey(Solicitante, on_delete=models.PROTECT, related_name='ordens')
    unidade = models.ForeignKey(Unidade, on_delete=models.PROTECT)
    centro_custo = models.ForeignKey(CentroCusto, on_delete=models.PROTECT)
    
    classificacao = models.CharField(max_length=10, choices=TIPO_CLASSIFICACAO)
    descricao_servico = models.TextField(verbose_name="Descrição do Material/Serviço")
    fornecedor = models.CharField(max_length=150)
    valor_estimado = models.DecimalField(max_digits=12, decimal_places=2)
    
    # Arquivos
    anexo_orcamento = models.FileField(upload_to='orcamentos/%Y/%m/', verbose_name="Orçamento (PDF)")

    # Controle
    data_criacao = models.DateTimeField(auto_now_add=True)
    data_atualizacao = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=20, choices=STATUS_PEDIDO, default='RASCUNHO')
    
    # Auditoria de Aprovação
    data_aprovacao = models.DateTimeField(null=True, blank=True)
    aprovado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='aprovacoes')
    motivo_reprovacao = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"OC #{self.pk} - {self.fornecedor} ({self.status})"

    def save(self, *args, **kwargs):
        # Lógica simples para travar edição se já estiver aprovado/concluído (opcional)
        super().save(*args, **kwargs)

# --- Módulo Financeiro (Auditoria e Recebimento) ---

class NotaFiscal(models.Model):
    """
    Auditoria: Garante que o pagamento bate com a Ordem de Compra.
    Relacionamento 1 para 1 garante que cada OC tenha sua finalização fiscal.
    """
    ordem_compra = models.OneToOneField(OrdemCompra, on_delete=models.CASCADE, related_name='nota_fiscal')
    
    numero_nf = models.CharField(max_length=50, verbose_name="Número da NF")
    numero_fluig = models.CharField(max_length=50, verbose_name="Número Fluig", help_text="ID do processo no Fluig se houver")
    data_emissao = models.DateField()
    arquivo_nf = models.FileField(upload_to='notas_fiscais/%Y/%m/')
    
    data_lancamento = models.DateTimeField(auto_now_add=True)
    responsavel_lancamento = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f"NF {self.numero_nf} ref. OC #{self.ordem_compra.pk}"

    def save(self, *args, **kwargs):
        # Ao salvar a NF, muda o status da Ordem para CONCLUIDO automaticamente
        super().save(*args, **kwargs)
        if self.ordem_compra.status != 'CONCLUIDO':
            self.ordem_compra.status = 'CONCLUIDO'
            self.ordem_compra.save()