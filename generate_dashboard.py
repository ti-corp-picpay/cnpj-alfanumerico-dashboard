#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Dashboard Generator - CPTECHC-491
Busca dados do Jira e gera HTML atualizado
"""

import os
import json
import base64
import sys
from datetime import datetime, timedelta
from collections import defaultdict
import requests

# Configuração via env vars
JIRA_EMAIL = os.getenv('JIRA_EMAIL')
JIRA_TOKEN = os.getenv('JIRA_TOKEN')
JIRA_BASE_URL = 'https://picpay.atlassian.net'
REQUEST_TIMEOUT = 30  # segundos

def get_jira_auth():
    """Retorna o header de autenticação Basic Auth"""
    credentials = f"{JIRA_EMAIL}:{JIRA_TOKEN}"
    encoded = base64.b64encode(credentials.encode()).decode()
    return {'Authorization': f'Basic {encoded}'}

def fetch_issues(jql, fields='key,summary,status,project,priority,duedate,assignee,resolutiondate,created,customfield_10021,customfield_10400'):
    """Busca issues do Jira com paginação"""
    # Usar o endpoint correto (não o /jql que dá 410)
    url = f"{JIRA_BASE_URL}/rest/api/2/search"
    all_issues = []
    seen_keys = set()
    
    params = {
        'jql': jql,
        'fields': fields,
        'maxResults': 100
    }
    
    headers = get_jira_auth()
    headers['Content-Type'] = 'application/json'
    
    print(f"  🔍 Endpoint: {url}", flush=True)
    print(f"  📝 JQL: {jql}", flush=True)
    
    page = 1
    while True:
        print(f"  📄 Buscando página {page}...", flush=True)
        try:
            response = requests.get(url, params=params, headers=headers, timeout=REQUEST_TIMEOUT)
            response.raise_for_status()
            data = response.json()
        except requests.exceptions.Timeout:
            print(f"  ⚠️ Timeout na página {page}, tentando novamente...", flush=True)
            continue
        except requests.exceptions.RequestException as e:
            print(f"  ❌ Erro na requisição: {e}", flush=True)
            print(f"  🔍 Response status: {response.status_code if 'response' in locals() else 'N/A'}", flush=True)
            raise
        
        issues_count = len(data.get('issues', []))
        
        if issues_count == 0:
            print(f"  🏁 Nenhuma issue retornada, finalizando", flush=True)
            break
        
        # Adicionar apenas issues únicas
        new_issues = 0
        for issue in data['issues']:
            issue_key = issue['key']
            if issue_key not in seen_keys:
                seen_keys.add(issue_key)
                all_issues.append(issue)
                new_issues += 1
        
        print(f"  ✅ {issues_count} issues retornadas, {new_issues} novas (total único: {len(all_issues)})", flush=True)
        
        # Se não vieram issues novas, parar
        if new_issues == 0:
            print(f"  🏁 Apenas duplicatas, finalizando", flush=True)
            break
        
        # Verificar se tem mais páginas (API v2 usa startAt + total)
        total = data.get('total', 0)
        start_at = data.get('startAt', 0)
        max_results = data.get('maxResults', 100)
        
        print(f"  🔍 startAt={start_at}, total={total}, maxResults={max_results}", flush=True)
        
        # Se já pegamos tudo, parar
        if start_at + max_results >= total:
            print(f"  🏁 Todas as issues coletadas", flush=True)
            break
        
        # Próxima página
        params['startAt'] = start_at + max_results
        page += 1
        
        if page > 10:
            print(f"  ⚠️ Limite de 10 páginas atingido", flush=True)
            break
    
    print(f"  📋 Total coletado: {len(all_issues)} issues únicas", flush=True)
    print(f"  🔑 Keys: {', '.join(sorted(seen_keys)[:20])}{'...' if len(seen_keys) > 20 else ''}", flush=True)
    return all_issues

def analyze_data():
    """Busca e analisa todos os dados necessários"""
    
    print("🔍 Buscando todas as issues da iniciativa CPTECHC-491...", flush=True)
    
    # Estratégia: buscar por squad para evitar limite de 100
    squads = ['PLD', 'COMFA', 'HCM', 'GEL', 'TICORP', 'MELCOR', 'EFCONT', 'CFERP']
    all_issues = []
    seen_keys = set()
    
    for squad in squads:
        jql = f'project = {squad} AND (parent = CPTECHC-491 OR parent IN portfolioChildIssuesOf("CPTECHC-491")) ORDER BY updated DESC'
        print(f"  🔍 Buscando issues do squad {squad}...", flush=True)
        
        try:
            squad_issues = fetch_issues(jql)
            # Adicionar apenas únicas
            new_count = 0
            for issue in squad_issues:
                if issue['key'] not in seen_keys:
                    seen_keys.add(issue['key'])
                    all_issues.append(issue)
                    new_count += 1
            print(f"     ✅ {new_count} issues novas do {squad}", flush=True)
        except Exception as e:
            print(f"     ⚠️ Erro ao buscar {squad}: {e}", flush=True)
            continue
    
    print(f"✅ Total de {len(all_issues)} issues únicas encontradas", flush=True)
    
    # Métricas básicas
    print("📊 Calculando métricas...", flush=True)
    total = len(all_issues)
    done = [i for i in all_issues if i['fields']['status']['name'] == 'Done']
    in_progress = [i for i in all_issues if i['fields']['status']['statusCategory']['key'] == 'indeterminate']
    backlog = [i for i in all_issues if i['fields']['status']['statusCategory']['key'] == 'new']
    cancelled = [i for i in all_issues if i['fields']['status']['name'] == 'Cancelled']
    
    # Issues pendentes
    pending = [i for i in all_issues if i['fields']['status']['name'] not in ['Done', 'Cancelled']]
    
    # Baseline vs Inject (criadas até 31/12/2025 vs depois)
    baseline_date = datetime(2025, 12, 31)
    baseline = [i for i in all_issues if datetime.fromisoformat(i['fields']['created'].replace('Z', '+00:00')).replace(tzinfo=None) <= baseline_date]
    inject = [i for i in all_issues if datetime.fromisoformat(i['fields']['created'].replace('Z', '+00:00')).replace(tzinfo=None) > baseline_date]
    
    # Issues sem due date (pendentes)
    no_duedate = [i for i in pending if not i['fields'].get('duedate')]
    
    # Por prioridade (pendentes)
    priority_counts = defaultdict(int)
    for issue in pending:
        priority = issue['fields'].get('priority')
        priority_name = priority.get('name', 'Sem prioridade') if priority else 'Sem prioridade'
        priority_counts[priority_name] += 1
    
    # Por squad (pendentes)
    squad_pending = defaultdict(int)
    squad_total = defaultdict(int)
    squad_done = defaultdict(int)
    
    for issue in all_issues:
        project = issue['fields']['project']['key']
        squad_total[project] += 1
        if issue['fields']['status']['name'] == 'Done':
            squad_done[project] += 1
    
    for issue in pending:
        project = issue['fields']['project']['key']
        squad_pending[project] += 1
    
    # Issues sem due date por squad
    no_duedate_by_squad = defaultdict(int)
    for issue in no_duedate:
        project = issue['fields']['project']['key']
        no_duedate_by_squad[project] += 1
    
    # Burndown (conclusões por mês)
    burndown = defaultdict(int)
    for issue in done:
        if issue['fields'].get('resolutiondate'):
            date = datetime.fromisoformat(issue['fields']['resolutiondate'].replace('Z', '+00:00'))
            month_key = date.strftime('%Y-%m')
            burndown[month_key] += 1
    
    # Issues com Flag (bloqueadas/impedidas)
    # Buscar diretamente com JQL ao invés de filtrar depois
    print("  🚩 Buscando issues com flag...", flush=True)
    flagged = []
    try:
        flag_jql = '(parent = CPTECHC-491 OR parent IN portfolioChildIssuesOf("CPTECHC-491")) AND Flagged IS NOT EMPTY'
        flag_issues = fetch_issues(flag_jql, fields='key,summary,status,project,priority')
        
        for issue in flag_issues:
            flagged.append({
                'key': issue['key'],
                'summary': issue['fields']['summary'],
                'status': issue['fields']['status']['name'],
                'squad': issue['fields']['project']['key'],
                'priority': issue['fields'].get('priority', {}).get('name', 'Sem prioridade') if issue['fields'].get('priority') else 'Sem prioridade'
            })
        
        print(f"  🚩 Issues com flag encontradas: {len(flagged)}", flush=True)
        if len(flagged) > 0:
            print(f"     Keys: {', '.join([f['key'] for f in flagged])}", flush=True)
    except Exception as e:
        print(f"  ⚠️ Erro ao buscar flags: {e}", flush=True)
        # Fallback: buscar manualmente nas issues conhecidas
        for issue in all_issues:
            if issue['key'] in ['HCM-788', 'MELCOR-212']:
                flagged.append({
                    'key': issue['key'],
                    'summary': issue['fields']['summary'],
                    'status': issue['fields']['status']['name'],
                    'squad': issue['fields']['project']['key'],
                    'priority': issue['fields'].get('priority', {}).get('name', 'Sem prioridade') if issue['fields'].get('priority') else 'Sem prioridade'
                })
        print(f"  🚩 Fallback: {len(flagged)} issues conhecidas com flag", flush=True)
    
    # Replanejamentos (lista manual, seria ideal buscar do changelog)
    replanned = [
        {'key': 'COMFA-702', 'times': 4, 'info': 'Dez/25 → Jun/26 (+5 meses)'},
        {'key': 'COMFA-698', 'times': 2, 'info': 'Fev/26 → Jun/26 (+3 meses)'},
        {'key': 'HCM-788', 'times': 2, 'info': 'Jan/26 → Abr/26 (+2.5 meses)'}
    ]
    
    return {
        'total': total,
        'done': len(done),
        'in_progress': len(in_progress),
        'backlog': len(backlog),
        'cancelled': len(cancelled),
        'pending': len(pending),
        'baseline': len(baseline),
        'inject': len(inject),
        'no_duedate': len(no_duedate),
        'no_duedate_by_squad': dict(no_duedate_by_squad),
        'priority_counts': dict(priority_counts),
        'squad_pending': dict(sorted(squad_pending.items(), key=lambda x: x[1], reverse=True)),
        'squad_total': dict(squad_total),
        'squad_done': dict(squad_done),
        'burndown': dict(sorted(burndown.items())),
        'flagged': flagged,
        'replanned': replanned,
        'generated_at': datetime.now().isoformat()
    }

def calculate_risks(data):
    """Calcula os níveis de risco"""
    print("⚠️ Calculando riscos...", flush=True)
    
    # Risco de Prazo
    months_remaining = 6  # até Jun/26
    pending = data['pending']
    
    # Velocidade média (últimos 3 meses)
    recent_burndown = list(data['burndown'].items())[-3:]
    avg_velocity = sum([count for _, count in recent_burndown]) / len(recent_burndown) if recent_burndown else 0
    
    # Velocidade necessária
    required_velocity = pending / months_remaining if months_remaining > 0 else 999
    
    # Classificação de risco de prazo
    velocity_ratio = avg_velocity / required_velocity if required_velocity > 0 else 1
    
    if velocity_ratio >= 1.2:
        deadline_risk = {'level': 'BAIXO', 'color': 'success', 'icon': 'check', 'avg_velocity': avg_velocity, 'required_velocity': required_velocity}
    elif velocity_ratio >= 0.8:
        deadline_risk = {'level': 'MEDIO', 'color': 'warning', 'icon': 'warning', 'avg_velocity': avg_velocity, 'required_velocity': required_velocity}
    else:
        deadline_risk = {'level': 'ALTO', 'color': 'danger', 'icon': 'alert', 'avg_velocity': avg_velocity, 'required_velocity': required_velocity}
    
    # Risco Operacional (issues críticas, sem due date)
    critical_count = data['priority_counts'].get('Highest', 0) + data['priority_counts'].get('High', 0)
    no_date_count = data['no_duedate']
    
    if critical_count >= 10 or no_date_count >= 15:
        operational_risk = {'level': 'ALTO', 'color': 'danger', 'icon': 'alert', 'critical_count': critical_count, 'no_date_count': no_date_count}
    elif critical_count >= 5 or no_date_count >= 8:
        operational_risk = {'level': 'MEDIO', 'color': 'warning', 'icon': 'warning', 'critical_count': critical_count, 'no_date_count': no_date_count}
    else:
        operational_risk = {'level': 'BAIXO', 'color': 'success', 'icon': 'check', 'critical_count': critical_count, 'no_date_count': no_date_count}
    
    print(f"  📊 Risco de Prazo: {deadline_risk['level']}", flush=True)
    print(f"  📊 Risco Operacional: {operational_risk['level']}", flush=True)
    
    return {
        'deadline': deadline_risk,
        'operational': operational_risk
    }

def main():
    """Função principal"""
    print("=" * 80, flush=True)
    print("Dashboard Generator - CPTECHC-491", flush=True)
    print("=" * 80, flush=True)
    
    # Validar env vars
    if not JIRA_EMAIL or not JIRA_TOKEN:
        print("❌ Erro: JIRA_EMAIL ou JIRA_TOKEN não configurado", flush=True)
        sys.exit(1)
    
    print(f"✅ JIRA_EMAIL: {JIRA_EMAIL}", flush=True)
    print(f"✅ JIRA_TOKEN: {'*' * 10}{JIRA_TOKEN[-4:]}", flush=True)
    
    try:
        # Buscar dados
        data = analyze_data()
        
        # Calcular riscos
        risk = calculate_risks(data)
        
        # Salvar JSON (debug)
        print("💾 Salvando dados em dashboard-data.json...", flush=True)
        with open('dashboard-data.json', 'w', encoding='utf-8') as f:
            json.dump({'data': data, 'risk': risk}, f, indent=2, ensure_ascii=False)
        print("💾 Dados salvos em dashboard-data.json", flush=True)
        
        # Gerar HTML
        print("🎨 Gerando HTML do dashboard...", flush=True)
        from html_generator import generate_html
        html_content = generate_html(data, risk)
        
        with open('dashboard.html', 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print("✅ dashboard.html gerado com sucesso!", flush=True)
        print("✅ Dashboard completo gerado com sucesso!", flush=True)
        
    except Exception as e:
        print(f"❌ Erro: {e}", flush=True)
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()
