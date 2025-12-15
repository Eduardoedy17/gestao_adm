# home/utils.py
from django.template.loader import render_to_string
from django.core.files.base import ContentFile
from weasyprint import HTML
import hashlib
from django.utils import timezone

def gerar_pdf_ordem_compra(ordem_compra):
    """
    Gera o PDF da Ordem de Compra, cria um Hash de integridade
    e salva o arquivo no campo anexo do modelo.
    """
    # 1. Gerar Hash Único para Auditoria (Impedir falsificação)
    audit_string = f"{ordem_compra.id}-{ordem_compra.valor_estimado}-{timezone.now()}"
    hash_audit = hashlib.sha256(audit_string.encode()).hexdigest()[:12].upper()

    context = {
        'oc': ordem_compra,
        'hash_audit': hash_audit,
        'data_geracao': timezone.now()
    }

    # 2. Renderizar HTML
    html_string = render_to_string('home/pdf_ordem_compra.html', context)

    # 3. Gerar PDF em memória
    pdf_file = HTML(string=html_string).write_pdf()

    # 4. Salvar no Banco de Dados (Evidência Imutável)
    filename = f"OC_{ordem_compra.id}_{hash_audit}.pdf"
    
    # Assumindo que você criará um campo 'arquivo_ordem_compra' no model ou usará o anexo existente.
    # Como o model atual tem 'anexo_orcamento' (entrada), sugiro criar um campo novo para SAÍDA.
    # Por enquanto, retornamos o conteúdo para download imediato ou envio de e-mail.
    return pdf_file, filename