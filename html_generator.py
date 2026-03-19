#!/usr/bin/env python3
"""
HTML Generator - CPTECHC-491 Dashboard
Transforma os dados do JSON em dashboard visual tema claro PicPay
"""

import json
from datetime import datetime

def generate_html(data, risk):
    """Gera o HTML completo do dashboard"""
    
    # Calcular mÃ©tricas derivadas
    progress_pct = round((data['done'] / data['total']) * 100) if data['total'] > 0 else 0
    inject_pct = round((data['inject'] / data['baseline']) * 100) if data['baseline'] > 0 else 0
    
    # Top 5 squads com mais issues pendentes
    top_squads = list(data['squad_pending'].items())[:5]
    
    # Issues sem due date - top 3 squads
    top_no_date = sorted(data['no_duedate_by_squad'].items(), key=lambda x: x[1], reverse=True)[:3]
    
    # Burndown - Ãºltimos 6 meses
    burndown_items = list(data['burndown'].items())[-6:]
    
    # Timestamp de atualizaÃ§Ã£o
    generated_at = datetime.fromisoformat(data['generated_at']).strftime('%d/%m/%Y %H:%M')
    
    html = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dashboard Executivo - CPTECHC-491</title>
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
            background: white;
            padding: 2rem;
            border-radius: 16px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.06);
            margin-bottom: 2rem;
            border-left: 6px solid #21C25E;
        }}
        
        h1 {{
            font-size: 2rem;
            font-weight: 700;
            color: #1a1a1a;
            margin-bottom: 0.5rem;
        }}
        
        .subtitle {{
            color: #6b7280;
            font-size: 0.95rem;
            display: flex;
            align-items: center;
            gap: 1rem;
            flex-wrap: wrap;
        }}
        
        .subtitle a {{
            color: #21C25E;
            text-decoration: none;
            font-weight: 500;
        }}
        
        .subtitle a:hover {{
            text-decoration: underline;
        }}
        
        .update-time {{
            font-size: 0.85rem;
            color: #9ca3af;
            margin-left: auto;
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
            font-size: 2rem;
        }}
        
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
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>ðŸ“Š Dashboard Executivo - CPTECHC-491</h1>
            <div class="subtitle">
                <span>Iniciativa: <strong>CNPJ AlfanumÃ©rico - AdequaÃ§Ãµes Multi-Squad</strong></span>
                <a href="https://picpay.atlassian.net/browse/CPTECHC-491" target="_blank">Ver no Jira â†’</a>
                <span class="update-time">Atualizado em: {generated_at}</span>
            </div>
        </header>
        
        <!-- KPIs Principais -->
        <div class="kpi-grid">
            <div class="kpi-card">
                <div class="kpi-label">Total de Issues</div>
                <div class="kpi-value">{data['total']}</div>
                <div class="kpi-detail">
                    <a href="https://picpay.atlassian.net/issues/?jql=parent%20%3D%20CPTECHC-491%20OR%20parent%20IN%20portfolioChildIssuesOf(%22CPTECHC-491%22)" target="_blank" class="link">Ver todas â†’</a>
                </div>
            </div>
            
            <div class="kpi-card">
                <div class="kpi-label">ConcluÃ­das</div>
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
                    <a href="https://picpay.atlassian.net/issues/?jql=parent%20%3D%20CPTECHC-491%20OR%20parent%20IN%20portfolioChildIssuesOf(%22CPTECHC-491%22)%20AND%20status%20NOT%20IN%20(Done%2C%20Cancelled)" target="_blank" class="link">Ver pendentes â†’</a>
                </div>
            </div>
            
            <div class="kpi-card">
                <div class="kpi-label">
                    <span class="tooltip" data-tooltip="Scope creep: issues criadas apÃ³s 31/12/2025">Inject (Scope Creep)</span>
                </div>
                <div class="kpi-value" style="color: #EF4444;">{data['inject']}</div>
                <div class="kpi-detail">+{inject_pct}% vs baseline ({data['baseline']})</div>
            </div>
        </div>
        
        <!-- FarÃ³is de Risco -->
        <div class="risk-grid">
            <div class="risk-card {risk['deadline']['color']}">
                <div class="risk-header">
                    <span class="risk-icon">{risk['deadline']['icon']}</span>
                    <div>
                        <div class="risk-title">Risco de Prazo</div>
                        <div class="risk-level {risk['deadline']['color']}">{risk['deadline']['level']}</div>
                    </div>
                </div>
                <div class="risk-detail">
                    Velocidade mÃ©dia: <strong>{risk['deadline']['avg_velocity']:.1f} issues/mÃªs</strong><br>
                    Velocidade necessÃ¡ria: <strong>{risk['deadline']['required_velocity']:.1f} issues/mÃªs</strong><br>
                    {data['pending']} issues restantes atÃ© Jun/26
                </div>
            </div>
            
            <div class="risk-card {risk['operational']['color']}">
                <div class="risk-header">
                    <span class="risk-icon">{risk['operational']['icon']}</span>
                    <div>
                        <div class="risk-title">Risco Operacional</div>
                        <div class="risk-level {risk['operational']['color']}">{risk['operational']['level']}</div>
                    </div>
                </div>
                <div class="risk-detail">
                    Issues crÃ­ticas: <strong>{risk['operational']['critical_count']}</strong><br>
                    Issues sem due date: <strong>{risk['operational']['no_date_count']}</strong><br>
                    Requer atenÃ§Ã£o imediata
                </div>
            </div>
        </div>
        
        <!-- Squads com Mais PendÃªncias -->
        <div class="section">
            <div class="section-title">ðŸŽ¯ Top 5 Squads - Issues Pendentes</div>
            <table>
                <thead>
                    <tr>
                        <th>Squad</th>
                        <th>Pendentes</th>
                        <th>Total</th>
                        <th>ConcluÃ­das</th>
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
                        <td><a href="{jql_link}" target="_blank" class="link">Ver issues â†’</a></td>
                    </tr>
"""
    
    html += """
                </tbody>
            </table>
        </div>
        
        <!-- Issues sem Due Date -->
        <div class="section">
            <div class="section-title">âš ï¸ Issues sem Due Date ({data['no_duedate']} no total)</div>
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
                        <td><a href="{jql_link}" target="_blank" class="link">Ver issues â†’</a></td>
                    </tr>
"""
    
    html += """
                </tbody>
            </table>
            <div style="margin-top: 1rem; color: #6b7280; font-size: 0.9rem;">
                ðŸ’¡ <strong>AÃ§Ã£o requerida:</strong> Agendar revisÃ£o com os squads para definir datas realistas.
            </div>
        </div>
        
        <!-- Burndown -->
        <div class="section">
            <div class="section-title">ðŸ“ˆ Burndown - Ãšltimos 6 Meses</div>
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
            <div class="section-title">ðŸ”„ Replanejamentos CrÃ­ticos</div>
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
                        <td><a href="{jql_link}" target="_blank" class="link">Ver issue â†’</a></td>
                    </tr>
"""
    
    html += """
                </tbody>
            </table>
            <div style="margin-top: 1rem; color: #6b7280; font-size: 0.9rem;">
                ðŸ’¡ <strong>AÃ§Ã£o requerida:</strong> Revisar impedimentos e dependÃªncias dessas issues.
            </div>
        </div>
        
        <footer>
            Dashboard gerado automaticamente via GitHub Actions<br>
            Dados atualizados diariamente Ã s 08h (horÃ¡rio de BrasÃ­lia)
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
    
    # Salvar
    with open('dashboard.html', 'w', encoding='utf-8') as f:
        f.write(html)
    
    print("âœ… dashboard.html gerado com sucesso!")
