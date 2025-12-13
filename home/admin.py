from django.contrib import admin
from .models import Unidade, CentroCusto, Solicitante, OrdemCompra, NotaFiscal

admin.site.register(Unidade)
admin.site.register(CentroCusto)
admin.site.register(Solicitante)
admin.site.register(OrdemCompra)
admin.site.register(NotaFiscal)