#!/usr/bin/env python3
"""Descobre qual campo o Jira usa para Flag"""

import os
import json
import base64
import requests

JIRA_EMAIL = os.getenv('JIRA_EMAIL', 'natali.lee@picpay.com')
JIRA_TOKEN = os.getenv('JIRA_TOKEN')
JIRA_BASE_URL = 'https://picpay.atlassian.net'

def get_jira_auth():
    credentials = f"{JIRA_EMAIL}:{JIRA_TOKEN}"
    encoded = base64.b64encode(credentials.encode()).decode()
    return {'Authorization': f'Basic {encoded}'}

def analyze_issue(issue_key):
    """Busca todos os campos de uma issue e mostra os não-vazios"""
    url = f"{JIRA_BASE_URL}/rest/api/2/issue/{issue_key}"
    headers = get_jira_auth()
    
    response = requests.get(url, headers=headers, timeout=30)
    if response.status_code != 200:
        print(f"❌ Erro ao buscar {issue_key}: {response.status_code}")
        return
    
    data = response.json()
    fields = data['fields']
    
    print(f"\n{'='*80}")
    print(f"🔍 Issue: {issue_key} - {fields.get('summary', 'N/A')}")
    print(f"{'='*80}")
    
    # Filtrar apenas campos não-vazios e relevantes
    relevant_fields = {}
    for key, value in fields.items():
        # Pular campos sempre vazios
        if value is None or value == '' or value == [] or value == {}:
            continue
        
        # Pular campos muito grandes (descrição, etc)
        if key in ['description', 'comment', 'worklog', 'attachment']:
            continue
            
        relevant_fields[key] = value
    
    print(f"\n📋 Campos não-vazios ({len(relevant_fields)}):")
    print("-" * 80)
    
    # Mostrar campos customizados primeiro (onde a flag provavelmente está)
    custom_fields = {k: v for k, v in relevant_fields.items() if k.startswith('customfield_')}
    other_fields = {k: v for k, v in relevant_fields.items() if not k.startswith('customfield_')}
    
    if custom_fields:
        print("\n🔧 CAMPOS CUSTOMIZADOS:")
        for key in sorted(custom_fields.keys()):
            value = custom_fields[key]
            value_str = json.dumps(value, indent=2, default=str) if isinstance(value, (dict, list)) else str(value)
            # Limitar tamanho da saída
            if len(value_str) > 200:
                value_str = value_str[:200] + "..."
            print(f"\n  {key}:")
            print(f"    {value_str}")
    
    print("\n📦 OUTROS CAMPOS RELEVANTES:")
    for key in sorted(other_fields.keys()):
        if key in ['summary', 'status', 'priority', 'project', 'issuetype']:
            continue  # já sabemos esses
        value = other_fields[key]
        value_str = json.dumps(value, indent=2, default=str) if isinstance(value, (dict, list)) else str(value)
        if len(value_str) > 200:
            value_str = value_str[:200] + "..."
        print(f"\n  {key}:")
        print(f"    {value_str}")

# Analisar as duas issues com flag
print("🚩 Analisando issues com flag...")
analyze_issue('HCM-788')
analyze_issue('MELCOR-212')

print("\n" + "="*80)
print("✅ Análise completa!")
print("="*80)
print("\n💡 Procure por campos que:")
print("   - Contêm 'flag', 'impediment', 'block' no nome")
print("   - Têm valores como 'Impediment', 'Blocked', arrays não-vazios")
print("   - Aparecem nas DUAS issues mas não em issues normais")
