"""
api_server.py — Full Working Backend + Dashboard
=================================================
Run:  python api_server.py
Open: http://localhost:8000
"""

import json
import os
import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()
from backend.db_manager import DBManager

log = logging.getLogger("api_server")
app = FastAPI(title="Jobs CRM", version="2.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
db = DBManager()

SMTP_EMAIL    = os.getenv("SMTP_FROM_EMAIL", "")
SMTP_PASSWORD = os.getenv("SMTP_APP_PASSWORD", "")


# ─────────────────────────────────────────────────────────────────────────────
# DASHBOARD HTML — served at http://localhost:8000
# ─────────────────────────────────────────────────────────────────────────────
DASHBOARD_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>Jobs CRM — Parameswar Swain</title>
<style>
*{box-sizing:border-box;margin:0;padding:0}
body{background:#09090b;color:#e4e4e7;font-family:'Segoe UI',system-ui,sans-serif;min-height:100vh}
a{color:inherit;text-decoration:none}
::-webkit-scrollbar{width:6px;height:6px}
::-webkit-scrollbar-track{background:#18181b}
::-webkit-scrollbar-thumb{background:#3f3f46;border-radius:3px}

.topbar{border-bottom:1px solid #27272a;padding:12px 24px;display:flex;align-items:center;justify-content:space-between;position:sticky;top:0;z-index:50;background:#09090b}
.topbar-left{display:flex;align-items:center;gap:10px}
.live-dot{width:8px;height:8px;border-radius:50%;background:#22c55e;animation:pulse 2s infinite}
.live-dot.dead{background:#ef4444;animation:none}
@keyframes pulse{0%,100%{opacity:1}50%{opacity:.3}}
.brand{font-size:13px;font-weight:700;letter-spacing:.08em;text-transform:uppercase}
.sub{font-size:11px;color:#52525b}
.topbar-right{display:flex;gap:8px;align-items:center}
.smtp-status{font-size:11px;padding:3px 8px;border-radius:4px;border:1px solid}
.smtp-ok{color:#86efac;border-color:#166534;background:#052e16}
.smtp-no{color:#fca5a5;border-color:#7f1d1d;background:#450a0a}

.btn{padding:7px 14px;border-radius:7px;font-size:12px;font-weight:600;cursor:pointer;border:1px solid;transition:all .15s;display:inline-flex;align-items:center;gap:5px}
.btn-ghost{background:#18181b;border-color:#3f3f46;color:#a1a1aa}
.btn-ghost:hover{background:#27272a;color:#e4e4e7}
.btn-violet{background:#5b21b6;border-color:#7c3aed;color:#ede9fe}
.btn-violet:hover{background:#6d28d9}
.btn-green{background:#14532d;border-color:#16a34a;color:#bbf7d0}
.btn-green:hover{background:#166534}
.btn-red{background:#450a0a;border-color:#dc2626;color:#fecaca}
.btn-red:hover{background:#7f1d1d}
.btn-sm{padding:4px 10px;font-size:11px}
.btn:disabled{opacity:.4;cursor:not-allowed}

.content{padding:20px 24px;max-width:1400px;margin:0 auto}

.stats{display:grid;grid-template-columns:repeat(5,1fr);gap:12px;margin-bottom:20px}
.stat{background:#18181b;border:1px solid #27272a;border-radius:10px;padding:14px 16px;cursor:pointer;transition:border .15s}
.stat:hover{border-color:#3f3f46}
.stat.active{border-color:#7c3aed}
.stat-val{font-size:28px;font-weight:700;font-variant-numeric:tabular-nums;line-height:1}
.stat-label{font-size:10px;color:#52525b;text-transform:uppercase;letter-spacing:.1em;margin-top:4px}

.toolbar{display:flex;gap:10px;margin-bottom:14px;flex-wrap:wrap;align-items:center}
.search-wrap{position:relative;flex:1;min-width:220px}
.search-icon{position:absolute;left:10px;top:50%;transform:translateY(-50%);color:#52525b;pointer-events:none}
input[type=text]{width:100%;background:#18181b;border:1px solid #3f3f46;border-radius:8px;padding:8px 10px 8px 32px;color:#e4e4e7;font-size:13px;outline:none;transition:border .15s}
input[type=text]:focus{border-color:#7c3aed}
select{background:#18181b;border:1px solid #3f3f46;border-radius:8px;padding:8px 12px;color:#d4d4d8;font-size:13px;outline:none;cursor:pointer}
.count-label{font-size:12px;color:#52525b;white-space:nowrap}

.table-wrap{background:#18181b;border:1px solid #27272a;border-radius:12px;overflow:hidden}
table{width:100%;border-collapse:collapse;font-size:13px}
thead tr{background:#111113;border-bottom:1px solid #27272a}
th{padding:10px 14px;text-align:left;font-size:10px;text-transform:uppercase;letter-spacing:.1em;color:#52525b;font-weight:700;white-space:nowrap}
tbody tr{border-bottom:1px solid #1f1f23;transition:background .1s;cursor:pointer}
tbody tr:hover{background:#1f1f23}
tbody tr:last-child{border-bottom:none}
tbody tr.selected{background:#1e1033}
td{padding:10px 14px;vertical-align:middle}

.company-name{font-weight:600;color:#fff;font-size:13px}
.company-meta{font-size:11px;color:#52525b;margin-top:1px}
.mode-icon{font-size:13px}
.stack-row{display:flex;flex-wrap:wrap;gap:3px;max-width:200px}
.tag{padding:2px 6px;border-radius:4px;font-size:10px;font-family:monospace;border:1px solid;white-space:nowrap}
.tag-react{background:#082f49;color:#7dd3fc;border-color:#0e4f7a}
.tag-next{background:#1c1c1e;color:#d4d4d8;border-color:#3f3f46}
.tag-ts{background:#0d1f3c;color:#93c5fd;border-color:#1e3a5f}
.tag-java{background:#2d1400;color:#fb923c;border-color:#7c2d00}
.tag-spring{background:#052e16;color:#86efac;border-color:#14532d}
.tag-node{background:#052e16;color:#4ade80;border-color:#166534}
.tag-gql{background:#2d0a1e;color:#f9a8d4;border-color:#831843}
.tag-py{background:#1e1b4b;color:#a5b4fc;border-color:#3730a3}
.tag-aws{background:#1c0a00;color:#fb923c;border-color:#7c2d00}
.tag-def{background:#1c1c1e;color:#71717a;border-color:#27272a}

.contact-name{color:#d4d4d8;font-size:13px}
.contact-title{font-size:11px;color:#52525b;margin-top:1px}
.email-pill{display:inline-flex;align-items:center;gap:4px;background:#1c1c1e;border:1px solid #27272a;border-radius:5px;padding:2px 7px;font-size:11px;color:#a1a1aa;margin-top:3px;max-width:200px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.conf-dot{width:5px;height:5px;border-radius:50%;flex-shrink:0}
.conf-hi{background:#22c55e}
.conf-lo{background:#f97316}

.score-wrap{display:flex;align-items:center;gap:6px}
.score-bar-bg{width:44px;height:4px;background:#27272a;border-radius:999px;overflow:hidden;flex-shrink:0}
.score-fill{height:100%;border-radius:999px;transition:width .3s}
.score-num{font-size:12px;color:#a1a1aa;font-variant-numeric:tabular-nums;min-width:24px}

.badge{padding:2px 8px;border-radius:4px;font-size:10px;font-weight:700;text-transform:uppercase;letter-spacing:.05em;white-space:nowrap}
.b-new{background:#27272a;color:#a1a1aa}
.b-researched{background:#1e3a5f;color:#93c5fd}
.b-draft{background:#451a03;color:#fcd34d}
.b-approved{background:#2e1065;color:#c4b5fd}
.b-sent{background:#083344;color:#67e8f9}
.b-replied{background:#052e16;color:#86efac}
.b-hired{background:#14532d;color:#dcfce7}
.b-other{background:#1c1c1e;color:#52525b}

.actions{display:flex;gap:6px;flex-wrap:wrap}
.empty-state{padding:60px 20px;text-align:center;color:#3f3f46}
.empty-state p{margin-top:8px;font-size:13px}

/* Side panel */
.layout{display:flex;gap:0}
.main-panel{flex:1;min-width:0}
.side-panel{width:480px;flex-shrink:0;border-left:1px solid #27272a;background:#0f0f11;display:none;position:sticky;top:53px;height:calc(100vh - 53px);overflow-y:auto}
.side-panel.open{display:block}
.side-header{padding:16px 20px;border-bottom:1px solid #27272a;display:flex;justify-content:space-between;align-items:flex-start;gap:10px}
.side-company{font-size:16px;font-weight:700;color:#fff}
.side-meta{font-size:12px;color:#52525b;margin-top:2px}
.close-btn{background:none;border:none;color:#52525b;font-size:18px;cursor:pointer;line-height:1;padding:2px;flex-shrink:0}
.close-btn:hover{color:#e4e4e7}
.side-body{padding:16px 20px}
.field-group{margin-bottom:16px}
.field-label{font-size:10px;color:#52525b;text-transform:uppercase;letter-spacing:.1em;margin-bottom:5px;display:flex;justify-content:space-between;align-items:center}
.field-val{font-size:13px;color:#d4d4d8}

textarea{width:100%;background:#09090b;border:1px solid #27272a;border-radius:8px;padding:10px 12px;font-size:13px;color:#d4d4d8;line-height:1.7;resize:vertical;outline:none;font-family:inherit;transition:border .15s}
textarea:focus{border-color:#7c3aed}
.subject-input{width:100%;background:#09090b;border:1px solid #27272a;border-radius:8px;padding:8px 12px;font-size:13px;color:#fff;font-weight:600;outline:none;transition:border .15s}
.subject-input:focus{border-color:#7c3aed}

.side-footer{padding:14px 20px;border-top:1px solid #27272a;display:flex;gap:8px;flex-wrap:wrap}

.toast{position:fixed;bottom:24px;right:24px;background:#18181b;border:1px solid #3f3f46;border-radius:10px;padding:12px 18px;font-size:13px;color:#e4e4e7;z-index:999;display:none;align-items:center;gap:8px;box-shadow:0 8px 32px rgba(0,0,0,.5);animation:slideUp .2s ease}
.toast.show{display:flex}
.toast.ok{border-color:#16a34a;background:#052e16;color:#86efac}
.toast.err{border-color:#dc2626;background:#450a0a;color:#fca5a5}
@keyframes slideUp{from{transform:translateY(10px);opacity:0}to{transform:translateY(0);opacity:1}}

.spinner{width:14px;height:14px;border:2px solid #3f3f46;border-top-color:#7c3aed;border-radius:50%;animation:spin .6s linear infinite;display:none}
@keyframes spin{to{transform:rotate(360deg)}}

@media(max-width:900px){
  .side-panel.open{position:fixed;inset:0;width:100%;height:100%;z-index:100;overflow-y:auto}
  .stats{grid-template-columns:repeat(2,1fr)}
  th:nth-child(3),td:nth-child(3){display:none}
}
</style>
</head>
<body>

<div class="topbar">
  <div class="topbar-left">
    <div class="live-dot" id="liveDot"></div>
    <span class="brand">CRM · Lead Engine</span>
    <span class="sub">Parameswar Swain · parameswar.dev</span>
  </div>
  <div class="topbar-right">
    <span class="smtp-status" id="smtpBadge">checking smtp…</span>
    <button class="btn btn-ghost" onclick="loadAll()">⟳ Refresh</button>
  </div>
</div>

<div class="tabs" style="border-bottom:1px solid #27272a;padding:0 24px;display:flex;gap:0;background:#09090b">
  <button class="tab-btn active" id="tab-leads" onclick="showTab('leads')" style="padding:10px 18px;background:none;border:none;border-bottom:2px solid #7c3aed;color:#e4e4e7;font-size:13px;font-weight:600;cursor:pointer;margin-bottom:-1px">📊 CRM Leads</button>
  <button class="tab-btn" id="tab-jobs" onclick="showTab('jobs')" style="padding:10px 18px;background:none;border:none;border-bottom:2px solid transparent;color:#71717a;font-size:13px;font-weight:600;cursor:pointer;margin-bottom:-1px">🔍 BBSR Hidden Jobs</button>
</div>

<div id="panel-leads" class="content">
  <!-- Stats -->
  <div class="stats" id="statsRow">
    <div class="stat" onclick="setFilter('all')"><div class="stat-val" id="sAll"  style="color:#e4e4e7">—</div><div class="stat-label">Total</div></div>
    <div class="stat" onclick="setFilter('leads')"><div class="stat-val" id="sLeads" style="color:#60a5fa">—</div><div class="stat-label">Leads</div></div>
    <div class="stat" onclick="setFilter('draft')"><div class="stat-val" id="sDraft" style="color:#fbbf24">—</div><div class="stat-label">Drafts</div></div>
    <div class="stat" onclick="setFilter('sent')"><div class="stat-val"  id="sSent"  style="color:#22d3ee">—</div><div class="stat-label">Sent</div></div>
    <div class="stat" onclick="setFilter('replied')"><div class="stat-val" id="sReply" style="color:#34d399">—</div><div class="stat-label">Replied</div></div>
  </div>

  <div class="layout">
    <div class="main-panel">
      <!-- Toolbar -->
      <div class="toolbar">
        <div class="search-wrap">
          <span class="search-icon">⌕</span>
          <input type="text" id="searchBox" placeholder="Search company, contact, email, stack…" oninput="render()"/>
        </div>
        <select id="modeFilter" onchange="render()">
          <option value="">All Modes</option>
          <option value="local">📍 Local</option>
          <option value="global">🌍 Remote</option>
        </select>
        <select id="statusFilter" onchange="render()">
          <option value="">All Statuses</option>
          <option value="researched">Researched</option>
          <option value="approved">Approved</option>
          <option value="sent">Sent</option>
          <option value="replied">Replied</option>
        </select>
        <span class="count-label" id="countLabel">— leads</span>
      </div>

      <!-- Table -->
      <div class="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Company</th>
              <th>Mode</th>
              <th>Stack</th>
              <th>Contact</th>
              <th>Score</th>
              <th>Status</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody id="tbody"></tbody>
        </table>
      </div>
    </div>

    <!-- Side panel -->
    <div class="side-panel" id="sidePanel">
      <div class="side-header">
        <div>
          <div class="side-company" id="spCompany"></div>
          <div class="side-meta" id="spMeta"></div>
        </div>
        <button class="close-btn" onclick="closePanel()">✕</button>
      </div>
      <div class="side-body">
        <div class="field-group">
          <div class="field-label">To</div>
          <div class="field-val" id="spTo"></div>
        </div>
        <div class="field-group">
          <div class="field-label">Subject <span style="color:#52525b;font-weight:400;text-transform:none">(editable)</span></div>
          <input class="subject-input" id="spSubject" type="text" placeholder="Email subject…"/>
        </div>
        <div class="field-group">
          <div class="field-label">Email Body <span style="color:#52525b;font-weight:400;text-transform:none">(editable)</span></div>
          <textarea id="spBody" rows="12" placeholder="Email body…"></textarea>
        </div>
        <div class="field-group">
          <div class="field-label">Stack</div>
          <div class="stack-row" id="spStack"></div>
        </div>
      </div>
      <div class="side-footer">
        <button class="btn btn-ghost btn-sm" onclick="copyDraft()">📋 Copy</button>
        <button class="btn btn-ghost btn-sm" onclick="saveDraft()">💾 Save</button>
        <button class="btn btn-violet btn-sm" id="approveBtn" onclick="approveLead()">✓ Approve</button>
        <button class="btn btn-green btn-sm" id="sendBtn" onclick="sendEmail()">
          <span class="spinner" id="sendSpinner"></span>
          <span id="sendLabel">📤 Send Email</span>
        </button>
      </div>
    </div>
  </div>
</div><!-- end panel-leads -->

<!-- BBSR Jobs Panel -->
<div id="panel-jobs" style="display:none;padding:20px 24px;max-width:1400px;margin:0 auto">
  <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:16px;flex-wrap:wrap;gap:10px">
    <div>
      <h2 style="font-size:16px;font-weight:700;color:#fff">🔍 BBSR Hidden Job Hunter</h2>
      <p style="font-size:12px;color:#52525b;margin-top:3px">Jobs from company websites, ATS portals, Google dorks — not just Naukri</p>
    </div>
    <button class="btn btn-ghost" onclick="loadBbsrJobs()">⟳ Refresh</button>
  </div>

  <!-- Category filters -->
  <div style="display:flex;gap:8px;margin-bottom:14px;flex-wrap:wrap;align-items:center">
    <div class="search-wrap" style="max-width:280px">
      <span class="search-icon">⌕</span>
      <input type="text" id="bbsr-search" placeholder="Search jobs…" oninput="renderBbsrJobs()"/>
    </div>
    <div style="display:flex;gap:6px;flex-wrap:wrap">
      <button class="btn btn-ghost btn-sm" onclick="bbsrFilter='all';renderBbsrJobs()">All</button>
      <button class="btn btn-ghost btn-sm" onclick="bbsrFilter='hidden';renderBbsrJobs()" style="color:#c4b5fd;border-color:#5b21b6">🔒 Hidden</button>
      <button class="btn btn-ghost btn-sm" onclick="bbsrFilter='frontend';renderBbsrJobs()" style="color:#7dd3fc">React/Frontend</button>
      <button class="btn btn-ghost btn-sm" onclick="bbsrFilter='java';renderBbsrJobs()" style="color:#fb923c">Java</button>
      <button class="btn btn-ghost btn-sm" onclick="bbsrFilter='sql';renderBbsrJobs()" style="color:#93c5fd">SQL/DB</button>
      <button class="btn btn-ghost btn-sm" onclick="bbsrFilter='fullstack';renderBbsrJobs()" style="color:#a5b4fc">Full Stack</button>
      <button class="btn btn-ghost btn-sm" onclick="bbsrFilter='backend';renderBbsrJobs()" style="color:#86efac">Backend</button>
    </div>
    <span style="font-size:12px;color:#52525b" id="bbsr-count">— jobs</span>
  </div>

  <!-- Jobs table -->
  <div class="table-wrap">
    <table>
      <thead>
        <tr>
          <th>Job Title</th>
          <th>Company</th>
          <th>Skills</th>
          <th>Category</th>
          <th>Salary</th>
          <th>Apply</th>
        </tr>
      </thead>
      <tbody id="bbsr-tbody">
        <tr><td colspan="6" class="empty-state">Click refresh or run python run.py → [J] first</td></tr>
      </tbody>
    </table>
  </div>

  <p style="font-size:11px;color:#27272a;text-align:center;margin-top:16px">
    Click any row to open the job listing · Hidden jobs = not on Naukri/Indeed
  </p>
</div>

<div class="toast" id="toast"></div>

<script>
const API = '';  // same origin
let allLeads = [];
let active = null;
let statusQuickFilter = '';

const TAG_MAP = {
  'React':'tag-react','Next.js':'tag-next','TypeScript':'tag-ts',
  'Java':'tag-java','Spring Boot':'tag-spring','Node.js':'tag-node',
  'GraphQL':'tag-gql','Python':'tag-py','AWS':'tag-aws',
  'Django':'tag-py','Postgres':'tag-def','MySQL':'tag-def',
  'MongoDB':'tag-def','Docker':'tag-def','Kubernetes':'tag-def',
};

const STATUS_MAP = {
  new:       ['b-new','New'],
  researched:['b-researched','Researched'],
  email_drafted:['b-draft','Draft'],
  approved:  ['b-approved','Approved'],
  sent:      ['b-sent','Sent'],
  replied:   ['b-replied','Replied ✓'],
  hired:     ['b-hired','HIRED 🎉'],
};

function scoreColor(s){ return s>=60?'#22c55e':s>=35?'#f59e0b':'#ef4444'; }

function tagHtml(t){
  const cls = TAG_MAP[t]||'tag-def';
  return `<span class="tag ${cls}">${t}</span>`;
}

function badgeHtml(s){
  const [cls,label] = STATUS_MAP[s]||['b-other',s||'?'];
  return `<span class="badge ${cls}">${label}</span>`;
}

function setFilter(f){
  statusQuickFilter = f;
  document.getElementById('statusFilter').value = '';
  render();
}

function filtered(){
  const q    = document.getElementById('searchBox').value.toLowerCase();
  const mode = document.getElementById('modeFilter').value;
  const st   = document.getElementById('statusFilter').value || statusQuickFilter;
  return allLeads.filter(l=>{
    const matchQ = !q ||
      (l.name||'').toLowerCase().includes(q) ||
      (l.full_name||'').toLowerCase().includes(q) ||
      (l.email||'').toLowerCase().includes(q) ||
      (l.job_title||'').toLowerCase().includes(q) ||
      (Array.isArray(l.tech_stack)?l.tech_stack:[]).some(t=>t.toLowerCase().includes(q));
    const matchM = !mode || l.mode===mode;
    const matchS = !st || st==='all' || l.status===st ||
      (st==='leads' && l.lead_id) ||
      (st==='draft' && l.draft_status==='draft') ||
      (st==='sent'  && l.draft_status==='sent');
    return matchQ && matchM && matchS;
  });
}

function render(){
  const rows = filtered();
  document.getElementById('countLabel').textContent = `${rows.length} of ${allLeads.length} leads`;
  const tbody = document.getElementById('tbody');
  if(!rows.length){
    tbody.innerHTML = `<tr><td colspan="7" class="empty-state">
      ${allLeads.length ? '🔍 No leads match your filters.' : '🚀 No leads yet — run <code>python run.py</code> to start hunting.'}
    </td></tr>`;
    return;
  }
  tbody.innerHTML = rows.map(l=>{
    const stack = Array.isArray(l.tech_stack)?l.tech_stack:[];
    const isActive = active && active.draft_id===l.draft_id;
    const conf = l.email_confidence||0;
    return `<tr onclick="openPanel(${l.draft_id||l.lead_id||l.company_id})" class="${isActive?'selected':''}">
      <td>
        <div class="company-name">${l.name||'?'}</div>
        <div class="company-meta">${l.funding_stage||''} ${l.hq_location?'· '+l.hq_location:''}</div>
      </td>
      <td><span class="mode-icon">${l.mode==='local'?'📍':'🌍'}</span></td>
      <td>
        <div class="stack-row">
          ${stack.slice(0,3).map(tagHtml).join('')}
          ${stack.length>3?`<span style="font-size:10px;color:#52525b">+${stack.length-3}</span>`:''}
        </div>
      </td>
      <td>
        <div class="contact-name">${l.full_name||'<span style="color:#3f3f46">—</span>'}</div>
        <div class="contact-title">${l.job_title||''}</div>
        ${l.email?`<div class="email-pill">
          <span class="conf-dot ${conf>=0.9?'conf-hi':'conf-lo'}"></span>
          ${l.email}
        </div>`:''}
      </td>
      <td>
        <div class="score-wrap">
          <div class="score-bar-bg"><div class="score-fill" style="width:${l.score||0}%;background:${scoreColor(l.score||0)}"></div></div>
          <span class="score-num">${l.score||0}</span>
        </div>
      </td>
      <td>${badgeHtml(l.status)}</td>
      <td>
        <div class="actions">
          ${l.subject?`<button class="btn btn-ghost btn-sm" onclick="event.stopPropagation();openPanel(${l.draft_id||l.lead_id||l.company_id})">Draft ↗</button>`:''}
          ${l.draft_status==='approved'?`<button class="btn btn-green btn-sm" onclick="event.stopPropagation();quickSend(${l.draft_id})">Send</button>`:''}
        </div>
      </td>
    </tr>`;
  }).join('');
}

function findLead(id){
  return allLeads.find(l=>l.draft_id===id||l.lead_id===id||l.company_id===id);
}

function openPanel(id){
  const l = findLead(id);
  if(!l) return;
  active = l;
  const stack = Array.isArray(l.tech_stack)?l.tech_stack:[];
  const conf = l.email_confidence||0;
  document.getElementById('spCompany').textContent = l.name||'?';
  document.getElementById('spMeta').textContent =
    [l.funding_stage, l.hq_location, l.mode==='local'?'📍 Local':'🌍 Remote'].filter(Boolean).join(' · ');
  document.getElementById('spTo').innerHTML = l.email
    ? `<span class="email-pill"><span class="conf-dot ${conf>=0.9?'conf-hi':'conf-lo'}"></span>${l.email}</span>
       <span style="font-size:12px;color:#52525b;margin-left:6px">${l.full_name||''} · ${l.job_title||''}</span>`
    : `<span style="color:#52525b">No email found — find on LinkedIn</span>`;
  document.getElementById('spSubject').value = l.subject||'';
  document.getElementById('spBody').value    = l.body_text||'';
  document.getElementById('spStack').innerHTML = stack.map(tagHtml).join('');
  const sp = document.getElementById('sidePanel');
  sp.classList.add('open');
  render();
}

function closePanel(){
  document.getElementById('sidePanel').classList.remove('open');
  active = null;
  render();
}

async function saveDraft(){
  if(!active||!active.draft_id) return toast('No draft to save','err');
  const subj = document.getElementById('spSubject').value;
  const body = document.getElementById('spBody').value;
  const r = await fetch(`/api/drafts/${active.draft_id}`,{
    method:'PUT',
    headers:{'Content-Type':'application/json'},
    body:JSON.stringify({subject:subj,body_text:body})
  });
  if(r.ok){ toast('Draft saved ✓','ok'); await loadAll(); }
  else toast('Save failed','err');
}

async function approveLead(){
  if(!active||!active.draft_id) return toast('No draft to approve','err');
  const r = await fetch(`/api/drafts/${active.draft_id}/approve`,{method:'POST'});
  if(r.ok){ toast('Approved! Ready to send.','ok'); await loadAll(); openPanel(active.draft_id); }
  else toast('Approve failed','err');
}

async function sendEmail(){
  if(!active) return;
  if(!active.email) return toast('No email address — find on LinkedIn first','err');
  const subj = document.getElementById('spSubject').value;
  const body = document.getElementById('spBody').value;
  if(!subj||!body) return toast('Subject and body cannot be empty','err');
  setLoading(true);
  const r = await fetch('/api/send',{
    method:'POST',
    headers:{'Content-Type':'application/json'},
    body:JSON.stringify({
      draft_id:  active.draft_id,
      to_email:  active.email,
      to_name:   active.full_name||'',
      subject:   subj,
      body_text: body
    })
  });
  setLoading(false);
  const data = await r.json();
  if(r.ok&&data.status==='sent'){ toast('Email sent! ✓','ok'); await loadAll(); openPanel(active.draft_id); }
  else toast(data.detail||'Send failed — check SMTP settings in .env','err');
}

async function quickSend(draftId){
  const l = findLead(draftId);
  if(!l||!l.email) return toast('No email address','err');
  setLoading(true);
  const r = await fetch('/api/send',{
    method:'POST',
    headers:{'Content-Type':'application/json'},
    body:JSON.stringify({
      draft_id: draftId,
      to_email: l.email,
      to_name:  l.full_name||'',
      subject:  l.subject||'',
      body_text:l.body_text||''
    })
  });
  setLoading(false);
  const data = await r.json();
  if(r.ok&&data.status==='sent'){ toast('Sent! ✓','ok'); await loadAll(); }
  else toast(data.detail||'Send failed','err');
}

function copyDraft(){
  const subj = document.getElementById('spSubject').value;
  const body = document.getElementById('spBody').value;
  navigator.clipboard.writeText(`Subject: ${subj}\\n\\n${body}`)
    .then(()=>toast('Copied to clipboard ✓','ok'));
}

function setLoading(on){
  document.getElementById('sendSpinner').style.display = on?'block':'none';
  document.getElementById('sendLabel').textContent     = on?'Sending…':'📤 Send Email';
  document.getElementById('sendBtn').disabled = on;
}

function toast(msg, type='ok'){
  const el = document.getElementById('toast');
  el.textContent = msg;
  el.className   = `toast show ${type}`;
  clearTimeout(window._toastTimer);
  window._toastTimer = setTimeout(()=>el.classList.remove('show'), 3500);
}

async function loadAll(){
  try{
    const [leads, stats, smtp] = await Promise.all([
      fetch('/api/leads').then(r=>r.json()),
      fetch('/api/stats').then(r=>r.json()),
      fetch('/api/smtp-status').then(r=>r.json()),
    ]);
    allLeads = leads;
    document.getElementById('sAll').textContent   = stats.companies||0;
    document.getElementById('sLeads').textContent = stats.leads||0;
    document.getElementById('sDraft').textContent = stats.drafts||0;
    document.getElementById('sSent').textContent  = stats.sent||0;
    document.getElementById('sReply').textContent = stats.replied||0;
    const dot = document.getElementById('liveDot');
    dot.classList.remove('dead');
    const smtpBadge = document.getElementById('smtpBadge');
    if(smtp.configured){
      smtpBadge.className='smtp-status smtp-ok';
      smtpBadge.textContent='✓ SMTP ready';
    } else {
      smtpBadge.className='smtp-status smtp-no';
      smtpBadge.textContent='✗ SMTP not set';
    }
    if(active) openPanel(active.draft_id||active.lead_id||active.company_id);
    render();
  } catch(e){
    document.getElementById('liveDot').classList.add('dead');
    document.getElementById('tbody').innerHTML=
      `<tr><td colspan="7" class="empty-state">⚠ API error — is <code>python api_server.py</code> running?</td></tr>`;
  }
}

document.addEventListener('keydown',e=>{if(e.key==='Escape')closePanel()});
loadAll();
setInterval(loadAll, 30000);

// ── Tab switching ─────────────────────────────────────────────────────────
function showTab(tab) {
  document.getElementById('panel-leads').style.display = tab==='leads' ? '' : 'none';
  document.getElementById('panel-jobs').style.display  = tab==='jobs'  ? '' : 'none';
  document.querySelectorAll('.tab-btn').forEach(b => {
    const isActive = b.id === 'tab-'+tab;
    b.style.borderBottomColor = isActive ? '#7c3aed' : 'transparent';
    b.style.color = isActive ? '#e4e4e7' : '#71717a';
  });
  if (tab === 'jobs') loadBbsrJobs();
}

// ── BBSR Jobs tab ─────────────────────────────────────────────────────────
let bbsrJobs = [];
let bbsrFilter = 'all';

async function loadBbsrJobs() {
  try {
    bbsrJobs = await fetch('/api/bbsr-jobs').then(r=>r.json());
    renderBbsrJobs();
  } catch(e) {
    document.getElementById('bbsr-tbody').innerHTML =
      '<tr><td colspan="6" class="empty-state">Run <code>python run.py</code> → choose [J] to hunt jobs first.</td></tr>';
  }
}

function renderBbsrJobs() {
  const q = (document.getElementById('bbsr-search')||{value:''}).value.toLowerCase();
  const cat = bbsrFilter;
  const filtered = bbsrJobs.filter(j => {
    const matchQ = !q || (j.title||'').toLowerCase().includes(q) ||
      (j.company||'').toLowerCase().includes(q) ||
      (j.skills||[]).some(s=>s.toLowerCase().includes(q));
    const matchC = cat==='all' || (j.category||'').toLowerCase()===cat ||
      (cat==='hidden' && j.is_hidden);
    return matchQ && matchC;
  });

  const hidden  = filtered.filter(j=>j.is_hidden).length;
  const public_ = filtered.filter(j=>!j.is_hidden).length;
  document.getElementById('bbsr-count').textContent = `${filtered.length} jobs · ${hidden} hidden · ${public_} public`;

  const tbody = document.getElementById('bbsr-tbody');
  if (!filtered.length) {
    tbody.innerHTML = bbsrJobs.length
      ? '<tr><td colspan="6" class="empty-state">No jobs match your filter.</td></tr>'
      : '<tr><td colspan="6" class="empty-state">No jobs yet — run <code>python run.py → [J]</code> to hunt BBSR jobs.</td></tr>';
    return;
  }

  tbody.innerHTML = filtered.map(j => {
    const skillTags = (j.skills||[]).slice(0,4).map(s=>
      `<span class="tag tag-def" style="font-size:10px">${s}</span>`
    ).join('');
    const hiddenBadge = j.is_hidden
      ? '<span style="background:#2d1657;color:#c4b5fd;border:1px solid #5b21b6;padding:1px 6px;border-radius:4px;font-size:10px;font-weight:700">HIDDEN</span>'
      : '';
    const catColor = {
      'Frontend':'#082f49;color:#7dd3fc','Java':'#2d1400;color:#fb923c',
      'SQL':'#0d1f3c;color:#93c5fd','Backend':'#052e16;color:#86efac',
      'FullStack':'#1e1b4b;color:#a5b4fc','SWE':'#1c1c1e;color:#71717a',
    }[j.category] || '1c1c1e;color:#71717a';

    return `<tr onclick="window.open('${j.apply_url}','_blank')" style="cursor:pointer">
      <td>
        <div style="font-weight:600;color:#fff">${j.title}</div>
        <div style="font-size:11px;color:#52525b;margin-top:2px">${j.posted_date||''}</div>
      </td>
      <td><div style="color:#d4d4d8">${j.company}</div><div style="font-size:11px;color:#52525b">${j.location}</div></td>
      <td><div style="display:flex;flex-wrap:wrap;gap:3px">${skillTags}</div></td>
      <td><span style="background:#${catColor};padding:2px 7px;border-radius:4px;font-size:10px;font-weight:700">${j.category||'SWE'}</span></td>
      <td>${j.salary||'<span style="color:#3f3f46">—</span>'}</td>
      <td>
        <div style="display:flex;gap:5px;flex-wrap:wrap;align-items:center">
          ${hiddenBadge}
          <a href="${j.apply_url}" target="_blank" class="btn btn-violet btn-sm" onclick="event.stopPropagation()">Apply ↗</a>
          <span style="font-size:10px;color:#52525b">${j.source}</span>
        </div>
      </td>
    </tr>`;
  }).join('');
}
</script>
</body>
</html>"""


# ─────────────────────────────────────────────────────────────────────────────
# MODELS
# ─────────────────────────────────────────────────────────────────────────────
class UpdateDraftRequest(BaseModel):
    subject:   str
    body_text: str

class SendRequest(BaseModel):
    draft_id:  int
    to_email:  str
    to_name:   str = ""
    subject:   str
    body_text: str


# ─────────────────────────────────────────────────────────────────────────────
# ROUTES
# ─────────────────────────────────────────────────────────────────────────────
@app.get("/", response_class=HTMLResponse)
def serve_dashboard():
    return HTMLResponse(DASHBOARD_HTML)

@app.get("/api/leads")
def get_leads():
    rows = db.get_all_leads()
    for r in rows:
        try:
            r["tech_stack"] = json.loads(r["tech_stack"]) if r["tech_stack"] else []
        except Exception:
            r["tech_stack"] = []
    return rows

@app.get("/api/stats")
def get_stats():
    s = db.get_stats()
    return {
        "companies": s["companies"],
        "leads":     s["leads"],
        "drafts":    s["drafts"],
        "sent":      s["sent"],
        "replied":   s["replied"],
    }

@app.get("/api/smtp-status")
def smtp_status():
    return {"configured": bool(SMTP_EMAIL and SMTP_PASSWORD)}

@app.put("/api/drafts/{draft_id}")
def update_draft(draft_id: int, req: UpdateDraftRequest):
    conn = db.connect()
    try:
        conn.execute(
            "UPDATE email_drafts SET subject=?, body_text=? WHERE id=?",
            (req.subject, req.body_text, draft_id),
        )
        conn.commit()
        return {"status": "updated"}
    finally:
        conn.close()

@app.post("/api/drafts/{draft_id}/approve")
def approve_draft(draft_id: int):
    ok = db.approve_draft(draft_id)
    if not ok:
        raise HTTPException(400, "Approval failed")
    return {"status": "approved"}

@app.post("/api/send")
def send_email(req: SendRequest):
    if not SMTP_EMAIL or not SMTP_PASSWORD:
        raise HTTPException(400, "SMTP not configured — add SMTP_FROM_EMAIL and SMTP_APP_PASSWORD to .env")
    if not req.to_email or "@" not in req.to_email:
        raise HTTPException(400, "Invalid email address")
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = req.subject
        msg["From"]    = f"Parameswar Swain <{SMTP_EMAIL}>"
        msg["To"]      = req.to_email
        msg["Reply-To"] = SMTP_EMAIL

        # Plain text
        plain = req.body_text
        # Simple HTML version
        html_body = req.body_text.replace("\n", "<br>")
        html = f"""<html><body style="font-family:Arial,sans-serif;font-size:14px;color:#111;line-height:1.7;max-width:600px;margin:0 auto;padding:20px">
{html_body}
</body></html>"""
        msg.attach(MIMEText(plain, "plain"))
        msg.attach(MIMEText(html,  "html"))

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(SMTP_EMAIL, SMTP_PASSWORD)
            server.sendmail(SMTP_EMAIL, req.to_email, msg.as_string())

        db.mark_sent(req.draft_id)
        log.info(f"Email sent → {req.to_email}")
        return {"status": "sent"}

    except smtplib.SMTPAuthenticationError:
        raise HTTPException(401, "Gmail auth failed — check your App Password in .env")
    except smtplib.SMTPRecipientsRefused:
        raise HTTPException(400, f"Email address rejected: {req.to_email}")
    except Exception as e:
        log.error(f"SMTP error: {e}")
        raise HTTPException(500, f"Send failed: {str(e)}")



@app.get("/api/bbsr-jobs")
def get_bbsr_jobs():
    """Return latest BBSR hidden jobs from JSON file."""
    import os
    path = os.path.join(os.path.dirname(__file__), "bbsr_jobs_latest.json")
    if not os.path.exists(path):
        return []
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []


if __name__ == "__main__":
    import uvicorn
    print("\n  ✅ Dashboard → http://localhost:8000")
    print("  📋 API docs  → http://localhost:8000/docs\n")
    uvicorn.run(
        "api_server:app",
        host=os.getenv("API_HOST", "127.0.0.1"),
        port=int(os.getenv("API_PORT", "8000")),
        reload=True,
    )