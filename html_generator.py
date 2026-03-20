#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HTML Generator - CPTECHC-491 Dashboard
Transforma os dados do JSON em dashboard visual tema claro PicPay
"""

import json
from datetime import datetime
import html as html_lib

def generate_html(data, risk):
    """Gera o HTML completo do dashboard"""
    
    # Calcular métricas derivadas
    progress_pct = round((data['done'] / data['total']) * 100) if data['total'] > 0 else 0
    inject_pct = round((data['inject'] / data['baseline']) * 100) if data['baseline'] > 0 else 0
    no_duedate_total = data['no_duedate']
    
    # Top 5 squads com mais issues pendentes
    top_squads = list(data['squad_pending'].items())[:5]
    
    # Issues sem due date - top 3 squads
    top_no_date = sorted(data['no_duedate_by_squad'].items(), key=lambda x: x[1], reverse=True)[:3]
    
    # Burndown - últimos 6 meses
    burndown_items = list(data['burndown'].items())[-6:]
    
    # Timestamp de atualização
    generated_at = datetime.fromisoformat(data['generated_at']).strftime('%d/%m/%Y %H:%M')
    
    html = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CNPJ Alfanumérico - Dashboard TI CORP</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            background: linear-gradient(135deg, #f5f7fa 0%, #e8ecf1 100%);
            color: #1a1a1a;
            line-height: 1.6;
            padding: 2rem;
        }}
        
        .container {{
            max-width: 1400px;
            margin: 0 auto;
        }}
        
        header {{
            background: linear-gradient(135deg, #1e5128 0%, #2d6a4f 50%, #40916c 100%);
            color: white;
            padding: 2rem 2.5rem;
            border-radius: 16px;
            box-shadow: 0 8px 32px rgba(30, 81, 40, 0.3);
            margin-bottom: 2rem;
            position: relative;
        }}
        
        .header-top {{
            display: flex;
            align-items: center;
            gap: 20px;
            margin-bottom: 20px;
        }}
        
        .logo-container {{
            display: flex;
            align-items: center;
            gap: 12px;
            background: rgba(255, 255, 255, 0.15);
            padding: 12px 20px;
            border-radius: 8px;
            backdrop-filter: blur(10px);
        }}
        
        .logo-picpay {{
            width: 40px;
            height: 40px;
            background: white;
            border-radius: 8px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: 900;
            font-size: 1.2em;
            color: #21C25E;
        }}
        
        .bu-name {{
            font-size: 1.1em;
            font-weight: 600;
            letter-spacing: 0.5px;
        }}
        
        h1 {{
            font-size: 2.2em;
            font-weight: 700;
            color: white;
            margin-bottom: 12px;
            letter-spacing: -0.5px;
        }}
        
        h1 a {{
            color: white;
            text-decoration: none;
            border-bottom: 2px solid rgba(255, 255, 255, 0.3);
            transition: border-color 0.3s ease;
        }}
        
        h1 a:hover {{
            border-bottom-color: rgba(255, 255, 255, 0.8);
        }}
        
        .subtitle {{
            color: rgba(255, 255, 255, 0.95);
            font-size: 1.05em;
            line-height: 1.6;
            max-width: 900px;
        }}
        
        .timestamp {{
            margin-top: 16px;
            font-size: 0.9em;
            color: rgba(255, 255, 255, 0.8);
            font-style: italic;
        }}
        
        .kpi-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
            gap: 1.5rem;
            margin-bottom: 2rem;
        }}
        
        .kpi-card {{
            background: white;
            padding: 1.5rem;
            border-radius: 12px;
            box-shadow: 0 2px 6px rgba(0,0,0,0.05);
            transition: transform 0.2s, box-shadow 0.2s;
        }}
        
        .kpi-card:hover {{
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        }}
        
        .kpi-label {{
            font-size: 0.85rem;
            color: #6b7280;
            font-weight: 500;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 0.5rem;
        }}
        
        .kpi-value {{
            font-size: 2.5rem;
            font-weight: 700;
            color: #1a1a1a;
            margin-bottom: 0.25rem;
        }}
        
        .kpi-detail {{
            font-size: 0.9rem;
            color: #6b7280;
        }}
        
        .progress-bar {{
            width: 100%;
            height: 12px;
            background: #e5e7eb;
            border-radius: 6px;
            overflow: hidden;
            margin-top: 0.5rem;
        }}
        
        .progress-fill {{
            height: 100%;
            background: linear-gradient(90deg, #21C25E 0%, #1a9b4d 100%);
            transition: width 0.5s ease;
        }}
        
        .risk-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 1.5rem;
            margin-bottom: 2rem;
        }}
        
        .risk-card {{
            background: white;
            padding: 1.5rem;
            border-radius: 12px;
            box-shadow: 0 2px 6px rgba(0,0,0,0.05);
            border-left: 4px solid;
        }}
        
        .risk-card.success {{ border-left-color: #21C25E; }}
        .risk-card.warning {{ border-left-color: #F59E0B; }}
        .risk-card.danger {{ border-left-color: #EF4444; }}
        
        .risk-header {{
            display: flex;
            align-items: center;
            gap: 0.75rem;
            margin-bottom: 1rem;
        }}
        
        .risk-icon {{
            font-size: 2.5rem;
            width: 48px;
            height: 48px;
            display: flex;
            align-items: center;
            justify-content: center;
            border-radius: 50%;
        }}
        
        .risk-icon.success {{ background: #D1FAE5; color: #21C25E; }}
        .risk-icon.warning {{ background: #FEF3C7; color: #F59E0B; }}
        .risk-icon.danger {{ background: #FEE2E2; color: #EF4444; }}
        
        .risk-icon.success::before {{ content: '✓'; }}
        .risk-icon.warning::before {{ content: '⚠'; }}
        .risk-icon.danger::before {{ content: '✕'; }}
        
        .risk-title {{
            font-size: 1.1rem;
            font-weight: 600;
            color: #1a1a1a;
        }}
        
        .risk-level {{
            font-size: 1.5rem;
            font-weight: 700;
            margin-bottom: 0.5rem;
        }}
        
        .risk-level.success {{ color: #21C25E; }}
        .risk-level.warning {{ color: #F59E0B; }}
        .risk-level.danger {{ color: #EF4444; }}
        
        .risk-detail {{
            font-size: 0.9rem;
            color: #6b7280;
            line-height: 1.5;
        }}
        
        .section {{
            background: white;
            padding: 2rem;
            border-radius: 12px;
            box-shadow: 0 2px 6px rgba(0,0,0,0.05);
            margin-bottom: 2rem;
        }}
        
        .section-title {{
            font-size: 1.3rem;
            font-weight: 700;
            color: #1a1a1a;
            margin-bottom: 1.5rem;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }}
        
        .section-title::before {{
            content: '';
            width: 4px;
            height: 24px;
            background: #21C25E;
            border-radius: 2px;
        }}
        
        table {{
            width: 100%;
            border-collapse: collapse;
        }}
        
        th {{
            text-align: left;
            padding: 0.75rem;
            font-size: 0.85rem;
            font-weight: 600;
            color: #6b7280;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            border-bottom: 2px solid #e5e7eb;
        }}
        
        td {{
            padding: 0.75rem;
            border-bottom: 1px solid #f3f4f6;
        }}
        
        tr:hover {{
            background: #f9fafb;
        }}
        
        .squad-name {{
            font-weight: 600;
            color: #1a1a1a;
        }}
        
        .number {{
            font-weight: 600;
            color: #21C25E;
        }}
        
        .link {{
            color: #21C25E;
            text-decoration: none;
            font-size: 0.85rem;
            font-weight: 500;
        }}
        
        .link:hover {{
            text-decoration: underline;
        }}
        
        .chart {{
            margin-top: 1.5rem;
        }}
        
        .bar-chart {{
            display: flex;
            flex-direction: column;
            gap: 1rem;
        }}
        
        .bar-item {{
            display: flex;
            align-items: center;
            gap: 1rem;
        }}
        
        .bar-label {{
            min-width: 80px;
            font-size: 0.9rem;
            font-weight: 500;
            color: #4b5563;
        }}
        
        .bar {{
            flex: 1;
            height: 32px;
            background: #e5e7eb;
            border-radius: 6px;
            overflow: hidden;
            position: relative;
        }}
        
        .bar-fill {{
            height: 100%;
            background: linear-gradient(90deg, #21C25E 0%, #1a9b4d 100%);
            display: flex;
            align-items: center;
            justify-content: flex-end;
            padding-right: 0.75rem;
            color: white;
            font-weight: 600;
            font-size: 0.85rem;
            transition: width 0.5s ease;
        }}
        
        .tooltip {{
            position: relative;
            display: inline-block;
            cursor: help;
            border-bottom: 1px dotted #6b7280;
        }}
        
        .tooltip:hover::after {{
            content: attr(data-tooltip);
            position: absolute;
            bottom: 100%;
            left: 50%;
            transform: translateX(-50%);
            background: #1a1a1a;
            color: white;
            padding: 0.5rem 0.75rem;
            border-radius: 6px;
            font-size: 0.8rem;
            white-space: nowrap;
            z-index: 100;
            margin-bottom: 0.5rem;
        }}
        
        .badge {{
            display: inline-block;
            padding: 0.25rem 0.75rem;
            border-radius: 12px;
            font-size: 0.8rem;
            font-weight: 600;
        }}
        
        .badge.success {{
            background: #D1FAE5;
            color: #065F46;
        }}
        
        .badge.warning {{
            background: #FEF3C7;
            color: #92400E;
        }}
        
        .badge.danger {{
            background: #FEE2E2;
            color: #991B1B;
        }}
        
        footer {{
            text-align: center;
            margin-top: 3rem;
            padding: 2rem;
            color: #6b7280;
            font-size: 0.85rem;
        }}
        
        @media (max-width: 768px) {{
            body {{
                padding: 1rem;
            }}
            
            h1 {{
                font-size: 1.5rem;
            }}
            
            .kpi-grid {{
                grid-template-columns: 1fr;
            }}
            
            .risk-grid {{
                grid-template-columns: 1fr;
            }}
        }}
        
        /* Issues Bloqueadas */
        .blocked-issues-grid {{
            display: grid;
            gap: 16px;
        }}
        
        .blocked-issue-card {{
            background: linear-gradient(135deg, #fef2f2 0%, #fee2e2 100%);
            border-left: 4px solid #ef4444;
            padding: 20px;
            border-radius: 8px;
            transition: all 0.3s ease;
            cursor: pointer;
        }}
        
        .blocked-issue-card:hover {{
            transform: translateX(4px);
            box-shadow: 0 4px 16px rgba(239, 68, 68, 0.2);
        }}
        
        .blocked-issue-header {{
            display: flex;
            align-items: center;
            gap: 12px;
            margin-bottom: 12px;
        }}
        
        .blocked-issue-key {{
            font-size: 1.1em;
            font-weight: 700;
            color: #991b1b;
        }}
        
        .blocked-issue-squad {{
            font-size: 0.85em;
            padding: 4px 10px;
            background: rgba(239, 68, 68, 0.15);
            border-radius: 4px;
            color: #991b1b;
            font-weight: 600;
        }}
        
        .blocked-issue-priority {{
            font-size: 0.85em;
            padding: 4px 10px;
            background: white;
            border-radius: 4px;
            color: #991b1b;
            font-weight: 600;
            margin-left: auto;
        }}
        
        .blocked-issue-summary {{
            color: #7f1d1d;
            font-size: 0.95em;
            line-height: 1.5;
            margin-bottom: 8px;
        }}
        
        .blocked-issue-status {{
            font-size: 0.85em;
            color: #991b1b;
            opacity: 0.8;
        }}
        
        /* Distribuição por Squad */
        .squad-distribution {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }}
        
        .squad-card {{
            background: white;
            border-radius: 12px;
            padding: 20px;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
            transition: all 0.3s ease;
            cursor: pointer;
            border-left: 4px solid #21C25E;
        }}
        
        .squad-card:hover {{
            transform: translateY(-4px);
            box-shadow: 0 8px 20px rgba(0, 0, 0, 0.12);
        }}
        
        .squad-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 16px;
        }}
        
        .squad-name {{
            font-size: 1.3em;
            font-weight: 700;
            color: #1e5128;
        }}
        
        .squad-total {{
            font-size: 2em;
            font-weight: 700;
            color: #2d6a4f;
        }}
        
        .squad-breakdown {{
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 12px;
            margin-bottom: 12px;
        }}
        
        .squad-stat {{
            text-align: center;
            padding: 8px;
            background: #f8f9fa;
            border-radius: 6px;
        }}
        
        .squad-stat-value {{
            font-size: 1.4em;
            font-weight: 700;
        }}
        
        .squad-stat-label {{
            font-size: 0.8em;
            color: #64748b;
            margin-top: 2px;
        }}
        
        .squad-stat.done .squad-stat-value {{
            color: #21C25E;
        }}
        
        .squad-stat.pending .squad-stat-value {{
            color: #f59e0b;
        }}
        
        .squad-stat.cancelled .squad-stat-value {{
            color: #94a3b8;
        }}
        
        .squad-progress {{
            margin-top: 12px;
        }}
        
        .squad-progress-label {{
            font-size: 0.85em;
            color: #64748b;
            margin-bottom: 6px;
            display: flex;
            justify-content: space-between;
        }}
        
        .squad-progress-bar {{
            width: 100%;
            height: 8px;
            background: #e5e7eb;
            border-radius: 4px;
            overflow: hidden;
        }}
        
        .squad-progress-fill {{
            height: 100%;
            background: linear-gradient(90deg, #2d6a4f 0%, #52b788 100%);
            border-radius: 4px;
            transition: width 1s ease;
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <div class="header-top">
                <div class="logo-container">
                    <div class="logo-picpay">💚</div>
                    <div class="bu-name">TI CORP</div>
                </div>
            </div>
            <h1>
                <a href="https://picpay.atlassian.net/browse/CPTECHC-491" target="_blank" title="Ver iniciativa no Jira">
                    📊 CNPJ Alfanumérico
                </a>
            </h1>
            <div class="subtitle">
                Programa de adequação de todos os sistemas TI CORP ao novo formato de CNPJ alfanumérico (IN RFB nº 2.229/2024). Vigência a partir de julho/2026 — apenas novos registros.
            </div>
            <div class="timestamp">📅 Atualizado em: {generated_at} (Brasília)</div>
        </header>
        
        <!-- KPIs Principais -->
        <div class="kpi-grid">
            <div class="kpi-card">
                <div class="kpi-label">Total de Issues</div>
                <div class="kpi-value">{data['total']}</div>
                <div class="kpi-detail">
                    <a href="https://picpay.atlassian.net/issues/?jql=parent%20%3D%20CPTECHC-491%20OR%20parent%20IN%20portfolioChildIssuesOf(%22CPTECHC-491%22)" target="_blank" class="link">Ver todas →</a>
                </div>
            </div>
            
            <div class="kpi-card">
                <div class="kpi-label">Concluídas</div>
                <div class="kpi-value" style="color: #21C25E;">{data['done']}</div>
                <div class="kpi-detail">{progress_pct}% do total</div>
                <div class="progress-bar">
                    <div class="progress-fill" style="width: {progress_pct}%"></div>
                </div>
            </div>
            
            <div class="kpi-card">
                <div class="kpi-label">Pendentes</div>
                <div class="kpi-value" style="color: #F59E0B;">{data['pending']}</div>
                <div class="kpi-detail">
                    <a href="https://picpay.atlassian.net/issues/?jql=parent%20%3D%20CPTECHC-491%20OR%20parent%20IN%20portfolioChildIssuesOf(%22CPTECHC-491%22)%20AND%20status%20NOT%20IN%20(Done%2C%20Cancelled)" target="_blank" class="link">Ver pendentes →</a>
                </div>
            </div>
            
            <div class="kpi-card">
                <div class="kpi-label">
                    <span class="tooltip" data-tooltip="Scope creep: issues criadas após 31/12/2025">Inject (Scope Creep)</span>
                </div>
                <div class="kpi-value" style="color: #EF4444;">{data['inject']}</div>
                <div class="kpi-detail">+{inject_pct}% vs baseline ({data['baseline']})</div>
            </div>
        </div>
        
        <!-- Faróis de Risco -->
        <div class="risk-grid">
            <div class="risk-card {risk['deadline']['color']}">
                <div class="risk-header">
                    <span class="risk-icon {risk['deadline']['color']}"></span>
                    <div>
                        <div class="risk-title">Risco de Prazo</div>
                        <div class="risk-level {risk['deadline']['color']}">{risk['deadline']['level']}</div>
                    </div>
                </div>
                <div class="risk-detail">
                    Velocidade média: <strong>{risk['deadline']['avg_velocity']:.1f} issues/mês</strong><br>
                    Velocidade necessária: <strong>{risk['deadline']['required_velocity']:.1f} issues/mês</strong><br>
                    {data['pending']} issues restantes até Jun/26
                </div>
            </div>
            
            <div class="risk-card {risk['operational']['color']}">
                <div class="risk-header">
                    <span class="risk-icon {risk['operational']['color']}"></span>
                    <div>
                        <div class="risk-title">Risco Operacional</div>
                        <div class="risk-level {risk['operational']['color']}">{risk['operational']['level']}</div>
                    </div>
                </div>
                <div class="risk-detail">
                    Issues críticas: <strong>{risk['operational']['critical_count']}</strong><br>
                    Issues sem due date: <strong>{risk['operational']['no_date_count']}</strong><br>
                    Requer atenção imediata
                </div>
            </div>
        </div>
        
        <!-- Squads com Mais Pendências -->
        <div class="section">
            <div class="section-title">🎯 Top 5 Squads - Issues Pendentes</div>
            <table>
                <thead>
                    <tr>
                        <th>Squad</th>
                        <th>Pendentes</th>
                        <th>Total</th>
                        <th>Concluídas</th>
                        <th>% Completo</th>
                        <th></th>
                    </tr>
                </thead>
                <tbody>
"""
    
    # Top squads
    for squad, pending in top_squads:
        total = data['squad_total'].get(squad, 0)
        done = data['squad_done'].get(squad, 0)
        pct = round((done / total) * 100) if total > 0 else 0
        jql_link = f"https://picpay.atlassian.net/issues/?jql=project%20%3D%20{squad}%20AND%20(parent%20%3D%20CPTECHC-491%20OR%20parent%20IN%20portfolioChildIssuesOf(%22CPTECHC-491%22))%20AND%20status%20NOT%20IN%20(Done%2C%20Cancelled)"
        
        html += f"""
                    <tr>
                        <td class="squad-name">{squad}</td>
                        <td><span class="number">{pending}</span></td>
                        <td>{total}</td>
                        <td>{done}</td>
                        <td>{pct}%</td>
                        <td><a href="{jql_link}" target="_blank" class="link">Ver issues →</a></td>
                    </tr>
"""
    
    html += """
                </tbody>
            </table>
        </div>
        
        <!-- Issues sem Due Date -->
        <div class="section">
            <div class="section-title">⚠️ Issues sem Due Date ({no_duedate_total} no total)</div>
            <table>
                <thead>
                    <tr>
                        <th>Squad</th>
                        <th>Issues sem Data</th>
                        <th></th>
                    </tr>
                </thead>
                <tbody>
"""
    
    # Issues sem due date
    for squad, count in top_no_date:
        jql_link = f"https://picpay.atlassian.net/issues/?jql=project%20%3D%20{squad}%20AND%20(parent%20%3D%20CPTECHC-491%20OR%20parent%20IN%20portfolioChildIssuesOf(%22CPTECHC-491%22))%20AND%20duedate%20is%20EMPTY%20AND%20status%20NOT%20IN%20(Done%2C%20Cancelled)"
        
        html += f"""
                    <tr>
                        <td class="squad-name">{squad}</td>
                        <td><span class="number">{count}</span></td>
                        <td><a href="{jql_link}" target="_blank" class="link">Ver issues →</a></td>
                    </tr>
"""
    
    html += """
                </tbody>
            </table>
            <div style="margin-top: 1rem; color: #6b7280; font-size: 0.9rem;">
                💡 <strong>Ação requerida:</strong> Agendar revisão com os squads para definir datas realistas.
            </div>
        </div>
        
        <!-- Burndown -->
        <div class="section">
            <div class="section-title">📈 Burndown - Últimos 6 Meses</div>
            <div class="chart bar-chart">
"""
    
    # Burndown chart
    max_value = max([v for k, v in burndown_items]) if burndown_items else 1
    for month, count in burndown_items:
        month_label = datetime.strptime(month, '%Y-%m').strftime('%b/%y')
        width_pct = (count / max_value) * 100 if max_value > 0 else 0
        
        html += f"""
                <div class="bar-item">
                    <div class="bar-label">{month_label}</div>
                    <div class="bar">
                        <div class="bar-fill" style="width: {width_pct}%">{count}</div>
                    </div>
                </div>
"""
    
    html += f"""
            </div>
        </div>
        
        <!-- Replanejamentos -->
        <div class="section">
            <div class="section-title">🔄 Replanejamentos Críticos</div>
            <table>
                <thead>
                    <tr>
                        <th>Issue</th>
                        <th>Vezes Replanejada</th>
                        <th>Impacto</th>
                        <th></th>
                    </tr>
                </thead>
                <tbody>
"""
    
    # Replanejamentos
    for item in data['replanned']:
        badge_class = 'danger' if item['times'] >= 4 else 'warning'
        jql_link = f"https://picpay.atlassian.net/browse/{item['key']}"
        
        html += f"""
                    <tr>
                        <td class="squad-name">{item['key']}</td>
                        <td><span class="badge {badge_class}">{item['times']}x</span></td>
                        <td>{item['info']}</td>
                        <td><a href="{jql_link}" target="_blank" class="link">Ver issue →</a></td>
                    </tr>
"""
    
    html += """
                </tbody>
            </table>
            <div style="margin-top: 1rem; color: #6b7280; font-size: 0.9rem;">
                💡 <strong>Ação requerida:</strong> Revisar impedimentos e dependências dessas issues.
            </div>
        </div>
        
        <!-- Issues Bloqueadas -->
        <div class="section">
            <div class="section-title">🚫 Issues Bloqueadas (Flagged)</div>
"""
    
    # Issues com flag
    if data.get('flagged') and len(data['flagged']) > 0:
        html += """
            <div class="blocked-issues-grid">
"""
        for issue in data['flagged']:
            jira_url = f"https://picpay.atlassian.net/browse/{issue['key']}"
            html += f"""
                <div class="blocked-issue-card" onclick="window.open('{jira_url}', '_blank')">
                    <div class="blocked-issue-header">
                        <div class="blocked-issue-key">{issue['key']}</div>
                        <div class="blocked-issue-squad">{issue['squad']}</div>
                        <div class="blocked-issue-priority">🔴 {issue['priority']}</div>
                    </div>
                    <div class="blocked-issue-summary">
                        {html_lib.escape(issue['summary'])}
                    </div>
                    <div class="blocked-issue-status">
                        Status: {issue['status']} | 🚩 Bloqueada
                    </div>
                </div>
"""
        html += """
            </div>
"""
    else:
        html += """
            <div style="text-align: center; padding: 40px; color: #6b7280;">
                🎉 Nenhuma issue bloqueada no momento!
            </div>
"""
    
    html += """
        </div>
        
        <!-- Distribuição por Squad -->
        <div class="section">
            <div class="section-title">🏢 Distribuição por Squad</div>
            <div style="margin-bottom: 20px; color: #64748b; font-size: 0.95rem;">
                Visão consolidada da hierarquia de issues por squad — identifique gargalos e acompanhe evolução
            </div>
            <div class="squad-distribution">
"""
    
    # Distribuição por squad
    for squad, total in sorted(data['squad_total'].items(), key=lambda x: x[1], reverse=True):
        done = data['squad_done'].get(squad, 0)
        pending = data['squad_pending'].get(squad, 0)
        cancelled = total - done - pending
        progress_pct = round((done / total) * 100) if total > 0 else 0
        
        jira_url = f"https://picpay.atlassian.net/issues/?jql=parent%20%3D%20CPTECHC-491%20OR%20parent%20IN%20portfolioChildIssuesOf(%22CPTECHC-491%22)%20AND%20project%20%3D%20{squad}"
        
        # Definir cor da borda baseado no progresso
        border_color = "#21C25E" if progress_pct >= 80 else "#f59e0b" if progress_pct >= 50 else "#ef4444"
        
        html += f"""
                <div class="squad-card" onclick="window.open('{jira_url}', '_blank')" style="border-left-color: {border_color};">
                    <div class="squad-header">
                        <div class="squad-name">{squad}</div>
                        <div class="squad-total">{total}</div>
                    </div>
                    <div class="squad-breakdown">
                        <div class="squad-stat done">
                            <div class="squad-stat-value">{done}</div>
                            <div class="squad-stat-label">✅ Done</div>
                        </div>
                        <div class="squad-stat pending">
                            <div class="squad-stat-value">{pending}</div>
                            <div class="squad-stat-label">⏳ Pendentes</div>
                        </div>
                        <div class="squad-stat cancelled">
                            <div class="squad-stat-value">{cancelled}</div>
                            <div class="squad-stat-label">❌ Canceladas</div>
                        </div>
                    </div>
                    <div class="squad-progress">
                        <div class="squad-progress-label">
                            <span>Progresso</span>
                            <span>{progress_pct}%</span>
                        </div>
                        <div class="squad-progress-bar">
                            <div class="squad-progress-fill" style="width: {progress_pct}%"></div>
                        </div>
                    </div>
                </div>
"""
    
    html += """
            </div>
        </div>
        
        <footer>
            Dashboard gerado automaticamente via GitHub Actions<br>
            Dados atualizados diariamente às 08h (horário de Brasília)
        </footer>
    </div>
</body>
</html>
"""
    
    return html

if __name__ == '__main__':
    # Ler dados do JSON
    with open('dashboard-data.json', 'r', encoding='utf-8') as f:
        json_data = json.load(f)
    
    data = json_data['data']
    risk = json_data['risk']
    
    # Gerar HTML
    html = generate_html(data, risk)
    
    # Salvar com UTF-8 (sem BOM, que é o padrão correto pra web)
    with open('dashboard.html', 'w', encoding='utf-8', newline='') as f:
        f.write(html)
    
    print("✅ dashboard.html gerado com sucesso!")
