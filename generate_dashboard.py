#!/usr/bin/env python3
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

# ConfiguraÃ§Ã£o via env vars
JIRA_EMAIL = os.getenv('JIRA_EMAIL')
JIRA_TOKEN = os.getenv('JIRA_TOKEN')
JIRA_BASE_URL = 'https://picpay.atlassian.net'
REQUEST_TIMEOUT = 30  # segundos

def get_jira_auth():
    """Retorna o header de autenticaÃ§Ã£o Basic Auth"""
    credentials = f"{JIRA_EMAIL}:{JIRA_TOKEN}"
    encoded = base64.b64encode(credentials.encode()).decode()
    return {'Authorization': f'Basic {encoded}'}

def fetch_issues(jql, fields='key,summary,status,project,priority,duedate,assignee,resolutiondate,created,customfield_10021'):
    """Busca issues do Jira com paginaÃ§Ã£o (customfield_10021 = Flagged)"""
    url = f"{JIRA_BASE_URL}/rest/api/2/search/jql"
    all_issues = []
    seen_keys = set()  # Para detectar duplicatas
    
    params = {
        'jql': jql,
        'fields': fields,
        'maxResults': 100
    }
    
    headers = get_jira_auth()
    headers['Content-Type'] = 'application/json'
    
    page = 1
    while True:
        print(f"  ðŸ“„ Buscando pÃ¡gina {page}...", flush=True)
        try:
            response = requests.get(url, params=params, headers=headers, timeout=REQUEST_TIMEOUT)
            response.raise_for_status()
            data = response.json()
        except requests.exceptions.Timeout:
            print(f"  âš ï¸ Timeout na pÃ¡gina {page}, tentando novamente...", flush=True)
            continue
        except requests.exceptions.RequestException as e:
            print(f"  âŒ Erro na requisiÃ§Ã£o: {e}", flush=True)
            raise
        
        issues_count = len(data.get('issues', []))
        
        # Verificar se nÃ£o vieram issues novas
        if issues_count == 0:
            print(f"  ðŸ Nenhuma issue retornada, finalizando", flush=True)
            break
        
        # Adicionar apenas issues Ãºnicas (sem duplicatas)
        new_issues = 0
        for issue in data['issues']:
            issue_key = issue['key']
            if issue_key not in seen_keys:
                seen_keys.add(issue_key)
                all_issues.append(issue)
                new_issues += 1
        
        print(f"  âœ… {issues_count} issues retornadas, {new_issues} novas (total Ãºnico: {len(all_issues)})", flush=True)
        
        # Se nÃ£o vieram issues novas, parar (API retornando duplicatas)
        if new_issues == 0:
            print(f"  ðŸ Apenas duplicatas retornadas, finalizando", flush=True)
            break
        
        if data.get('isLast', True):
            print(f"  ðŸ Ãšltima pÃ¡gina alcanÃ§ada", flush=True)
            break
        
        # PaginaÃ§Ã£o com nextPageToken (novo formato)
        if 'nextPageToken' in data:
            params['pageToken'] = data['nextPageToken']
            page += 1
        else:
            print(f"  ðŸ Sem nextPageToken, finalizando", flush=True)
            break
        
        # Limite de seguranÃ§a (mÃ¡ximo 50 pÃ¡ginas)
        if page > 50:
            print(f"  âš ï¸ Limite de 50 pÃ¡ginas atingido, abortando", flush=True)
            break
    
    return all_issues

def analyze_data():
    """Busca e analisa todos os dados necessÃ¡rios"""
    
    print("ðŸ” Buscando todas as issues da iniciativa CPTECHC-491...", flush=True)
    
    try:
        all_issues = fetch_issues('parent = CPTECHC-491 OR parent IN portfolioChildIssuesOf("CPTECHC-491")')
    except Exception as e:
        print(f"âŒ Erro ao buscar issues: {e}", flush=True)
        raise
    
    print(f"âœ… Total de {len(all_issues)} issues encontradas", flush=True)
    
    # MÃ©tricas bÃ¡sicas
    print("ðŸ“Š Calculando mÃ©tricas...", flush=True)
    total = len(all_issues)
    done = [i for i in all_issues if i['fields']['status']['name'] == 'Done']
    in_progress = [i for i in all_issues if i['fields']['status']['statusCategory']['key'] == 'indeterminate']
    backlog = [i for i in all_issues if i['fields']['status']['statusCategory']['key'] == 'new']
    cancelled = [i for i in all_issues if i['fields']['status']['name'] == 'Cancelled']
    
    # Issues pendentes
    pending = [i for i in all_issues if i['fields']['status']['name'] not in ['Done', 'Cancelled']]
    
    # Baseline vs Inject (criadas atÃ© 31/12/2025 vs depois)
    baseline_date = datetime(2025, 12, 31)
    baseline = [i for i in all_issues if datetime.fromisoformat(i['fields']['created'].replace('Z', '+00:00')).replace(tzinfo=None) <= baseline_date]
    inject = [i for i in all_issues if datetime.fromisoformat(i['fields']['created'].replace('Z', '+00:00')).replace(tzinfo=None) > baseline_date]
    
    # Issues sem due date (pendentes)
    no_duedate = [i for i in pending if not i['fields'].get('duedate')]
    
    # Por prioridade (pendentes)
    priority_counts = defaultdict(int)
    for issue in pending:
        priority = issue['fields'].get('priority', {})
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
    
    # Burndown (conclusÃµes por mÃªs)
    burndown = defaultdict(int)
    for issue in done:
        if issue['fields'].get('resolutiondate'):
            date = datetime.fromisoformat(issue['fields']['resolutiondate'].replace('Z', '+00:00'))
            month_key = date.strftime('%Y-%m')
            burndown[month_key] += 1
    
    # Issues com Flag (bloqueadas/impedidas)
    flagged = []
    for issue in all_issues:
        # Flag pode estar em customfield_10021 ou flagged
        flag_field = issue['fields'].get('customfield_10021') or issue['fields'].get('flagged')
        if flag_field:
            # Flag pode ser um array ou objeto
            has_flag = False
            if isinstance(flag_field, list) and len(flag_field) > 0:
                has_flag = True
            elif isinstance(flag_field, dict) and flag_field.get('value'):
                has_flag = True
            elif isinstance(flag_field, str) and flag_field:
                has_flag = True
            
            if has_flag:
                flagged.append({
                    'key': issue['key'],
                    'summary': issue['fields']['summary'],
                    'status': issue['fields']['status']['name'],
                    'squad': issue['fields']['project']['key'],
                    'priority': issue['fields'].get('priority', {}).get('name', 'Sem prioridade') if issue['fields'].get('priority') else 'Sem prioridade'
                })
    
    # Replanejamentos (lista manual, seria ideal buscar do changelog)
    replanned = [
        {'key': 'COMFA-702', 'times': 4, 'info': 'Dez/25 â†’ Jun/26 (+5 meses)'},
        {'key': 'COMFA-698', 'times': 2, 'info': 'Fev/26 â†’ Jun/26 (+3 meses)'},
        {'key': 'HCM-788', 'times': 2, 'info': 'Jan/26 â†’ Abr/26 (+2.5 meses)'}
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
        'replanned': replanned,
        'flagged': flagged,
        'generated_at': datetime.now().isoformat()
    }

def calculate_risk(data):
    """Calcula os indicadores de risco"""
    
    print("âš ï¸ Calculando riscos...", flush=True)
    
    # Risco de prazo
    months_remaining = 3  # atÃ© junho/26
    pending = data['pending']
    
    # MÃ©dia dos Ãºltimos 3 meses
    recent_months = list(data['burndown'].values())[-3:] if len(data['burndown']) >= 3 else list(data['burndown'].values())
    avg_velocity = sum(recent_months) / len(recent_months) if recent_months else 0
    
    required_velocity = pending / months_remaining if months_remaining > 0 else pending
    
    if avg_velocity >= required_velocity * 1.2:
        deadline_risk = 'BAIXO'
        deadline_color = 'success'
        deadline_icon = 'ðŸŸ¢'
    elif avg_velocity >= required_velocity * 0.8:
        deadline_risk = 'MÃ‰DIO'
        deadline_color = 'warning'
        deadline_icon = 'ðŸŸ¡'
    else:
        deadline_risk = 'ALTO'
        deadline_color = 'danger'
        deadline_icon = 'ðŸ”´'
    
    # Risco operacional
    critical_count = data['priority_counts'].get('Critical', 0)
    no_date_count = data['no_duedate']
    
    if critical_count >= 15 or no_date_count >= 10:
        operational_risk = 'ALTO'
        operational_color = 'danger'
        operational_icon = 'ðŸ”´'
    elif critical_count >= 8 or no_date_count >= 5:
        operational_risk = 'MÃ‰DIO'
        operational_color = 'warning'
        operational_icon = 'ðŸŸ¡'
    else:
        operational_risk = 'BAIXO'
        operational_color = 'success'
        operational_icon = 'ðŸŸ¢'
    
    return {
        'deadline': {
            'level': deadline_risk,
            'color': deadline_color,
            'icon': deadline_icon,
            'avg_velocity': avg_velocity,
            'required_velocity': required_velocity
        },
        'operational': {
            'level': operational_risk,
            'color': operational_color,
            'icon': operational_icon,
            'critical_count': critical_count,
            'no_date_count': no_date_count
        }
    }

if __name__ == '__main__':
    print("ðŸš€ Gerando Dashboard CPTECHC-491...", flush=True)
    print(f"â° Timestamp: {datetime.now().isoformat()}", flush=True)
    
    # Validar env vars
    if not JIRA_EMAIL or not JIRA_TOKEN:
        print("âŒ Erro: JIRA_EMAIL e JIRA_TOKEN devem estar definidos como variÃ¡veis de ambiente", flush=True)
        sys.exit(1)
    
    print(f"âœ… Credenciais configuradas (email: {JIRA_EMAIL[:3]}***)", flush=True)
    
    try:
        # Buscar e analisar dados
        data = analyze_data()
        print(f"âœ… AnÃ¡lise completa:", flush=True)
        print(f"   Total: {data['total']} issues", flush=True)
        print(f"   Done: {data['done']} | Pendentes: {data['pending']}", flush=True)
        print(f"   Baseline: {data['baseline']} | Inject: {data['inject']}", flush=True)
        
        # Calcular risco
        risk = calculate_risk(data)
        print(f"ðŸ“Š Risco de Prazo: {risk['deadline']['icon']} {risk['deadline']['level']}", flush=True)
        print(f"ðŸ“Š Risco Operacional: {risk['operational']['icon']} {risk['operational']['level']}", flush=True)
        
        # Salvar dados brutos
        output_file = 'dashboard-data.json'
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump({'data': data, 'risk': risk}, f, indent=2, ensure_ascii=False)
        print(f"ðŸ’¾ Dados salvos em {output_file}", flush=True)
        
        # Gerar HTML
        print("ðŸŽ¨ Gerando HTML do dashboard...", flush=True)
        from html_generator import generate_html
        html = generate_html(data, risk)
        with open('dashboard.html', 'w', encoding='utf-8') as f:
            f.write(html)
        print("âœ… dashboard.html gerado com sucesso!", flush=True)
        
        print("âœ… Dashboard completo gerado com sucesso!", flush=True)
        
    except Exception as e:
        print(f"âŒ Erro fatal: {e}", flush=True)
        import traceback
        traceback.print_exc()
        sys.exit(1)
