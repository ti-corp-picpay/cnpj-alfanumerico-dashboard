#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Gera preview do dashboard com dados simulados de dependencias"""

import json
import sys
sys.path.insert(0, '.')
from html_generator import generate_html

# Carregar dados reais
with open('preview-data.json', 'r', encoding='utf-8') as f:
    raw = json.load(f)

data = raw['data']
risk = raw['risk']

# Adicionar dependencias simuladas para preview
data['dependencies'] = [
    {
        'key': 'PROJ-123',
        'summary': 'Adequacao sistema legado para novo formato CNPJ alfanumerico',
        'status': 'In Progress',
        'status_color': 'indeterminate',
        'project': 'PROJ',
        'priority': 'High',
        'link_type': 'is blocked by',
        'linked_to': 'CPTECHC-491'
    },
    {
        'key': 'INFRA-456',
        'summary': 'Atualizar validacao de CNPJ nos microsservicos de cadastro',
        'status': 'To Do',
        'status_color': 'new',
        'project': 'INFRA',
        'priority': 'Critical',
        'link_type': 'blocks',
        'linked_to': 'CPTECHC-491'
    },
    {
        'key': 'DATA-789',
        'summary': 'Migrar tabelas de referencia para suportar CNPJ com 14 caracteres',
        'status': 'Done',
        'status_color': 'done',
        'project': 'DATA',
        'priority': 'Medium',
        'link_type': 'relates to',
        'linked_to': 'CPTECHC-491'
    },
    {
        'key': 'SEC-101',
        'summary': 'Validacao de seguranca para novo formato de documento',
        'status': 'In Review',
        'status_color': 'indeterminate',
        'project': 'SEC',
        'priority': 'High',
        'link_type': 'is blocked by',
        'linked_to': 'CPTECHC-491'
    }
]

# Gerar HTML
html = generate_html(data, risk)

# Salvar preview
output = r'C:\Users\NL159124\Downloads\dashboard-preview-deps.html'
with open(output, 'w', encoding='utf-8') as f:
    f.write(html)

print(f"Preview salvo em: {output}")
