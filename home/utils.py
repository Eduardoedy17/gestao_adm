from django.template.loader import render_to_string
import hashlib
from django.utils import timezone

def gerar_pdf_ordem_compra(ordem_compra):
    """
    Gera o PDF da Ordem de Compra.
    Usa 'Lazy Import' e tratamento de erro para não quebrar o deploy no Vercel.
    """
    # 1. Gerar Hash Único
    audit_string = f"{ordem_compra.id}-{ordem_compra.valor_estimado}-{timezone.now()}"
    hash_audit = hashlib.sha256(audit_string.encode()).hexdigest()[:12].upper()

    context = {
        'oc': ordem_compra,
        'hash_audit': hash_audit,
        'data_geracao': timezone.now()
    }

    html_string = render_to_string('home/pdf_ordem_compra.html', context)

    # 2. Tenta importar e gerar o PDF com segurança
    try:
        # IMPORTAÇÃO TARDIA: Só carrega a lib aqui dentro
        from weasyprint import HTML
        
        pdf_file = HTML(string=html_string).write_pdf()
        filename = f"OC_{ordem_compra.id}_{hash_audit}.pdf"
        return pdf_file, filename

    except OSError as e:
        # Se der erro de biblioteca (comum no Vercel), loga e retorna vazio
        print(f"Erro ao gerar PDF (WeasyPrint): {e}")
        return None, None
    except ImportError:
        print("WeasyPrint não está instalado ou falhou ao importar.")
        return None, None