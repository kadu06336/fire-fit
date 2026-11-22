<!doctype html>
<html lang="pt-BR">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Fire Fit</title>
  <style>
    * { box-sizing: border-box; font-family: system-ui, -apple-system, sans-serif; }
    body { margin: 0; background: #0f172a; color: #f8fafc; padding-bottom: 84px; }
    header { background: #1e293b; padding: 14px 16px; border-bottom: 1px solid #334155; position: sticky; top: 0; z-index: 10; }
    h1 { margin: 0; font-size: 1.2rem; color: #fb923c; }
    .aviso { font-size: 0.78rem; color: #cbd5e1; margin-top: 4px; }
    main { padding: 14px; max-width: 720px; margin: 0 auto; }
    .card { background: #1e293b; border: 1px solid #334155; border-radius: 12px; padding: 14px; margin-bottom: 12px; }
    .alerta-banner { background: #431407; border: 1px solid #ea580c; color: #fed7aa; border-radius: 12px; padding: 12px 14px; margin-bottom: 12px; font-size: 0.9rem; display: none; }
    .alerta-banner.ativo { display: block; }
    .alerta-kcal-box { padding: 12px; border-radius: 10px; font-size: 0.92rem; font-weight: 600; margin-top: 10px; border: 1px solid #475569; background: #0f172a; color: #e2e8f0; }
    .alerta-kcal-box.passou { background: #450a0a; border-color: #ef4444; color: #fecaca; }
    .alerta-kcal-box.faltando { background: #172554; border-color: #38bdf8; color: #bae6fd; }
    .alerta-kcal-box.na_meta { background: #052e16; border-color: #22c55e; color: #bbf7d0; }
    .grid-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }
    .grid-3 { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 8px; }
    label { display: block; font-size: 0.8rem; color: #94a3b8; margin-bottom: 4px; }
    input, select, button { width: 100%; padding: 10px; border-radius: 8px; border: 1px solid #475569; font-size: 0.95rem; }
    input, select { background: #0f172a; color: #f8fafc; margin-bottom: 10px; }
    button { background: #ea580c; color: #fff; border: none; font-weight: 600; cursor: pointer; }
    button:active { opacity: 0.85; }
    .btn-sec { background: #334155; color: #f8fafc; }
    .btn-ok { width: auto; background: #15803d; color: #dcfce7; font-size: 0.75rem; padding: 5px 9px; border-radius: 6px; margin-left: 6px; flex-shrink: 0; }
    .btn-del { width: auto; background: #991b1b; color: #fecaca; font-size: 0.75rem; padding: 5px 9px; border-radius: 6px; margin-left: 6px; flex-shrink: 0; }
    .acoes-item { display: flex; align-items: center; flex-shrink: 0; }
    .kpi { font-size: 1.15rem; font-weight: 700; color: #fdba74; }
    .barra-bg { width: 100%; height: 14px; background: #0f172a; border-radius: 999px; overflow: hidden; border: 1px solid #475569; margin: 6px 0 10px; }
    .barra-fill { height: 100%; background: #38bdf8; min-width: 6px; width: 6%; transition: width 0.25s; }
    .barra-saude { background: #22c55e; }
    .barra-treino { background: #fb923c; }
    .barra-kcal { background: #facc15; }
    .barra-kcal.passou { background: #ef4444; }
    .crono-display { font-size: 2rem; font-weight: 800; text-align: center; color: #fdba74; letter-spacing: 1px; margin: 6px 0 12px; font-variant-numeric: tabular-nums; }
    .sub { font-size: 0.88rem; color: #cbd5e1; margin-top: 6px; line-height: 1.35; }
    .calc-preview { font-size: 0.85rem; color: #86efac; background: #052e16; border: 1px solid #166534; border-radius: 8px; padding: 8px 10px; margin-bottom: 10px; }
    .item { display: flex; justify-content: space-between; align-items: center; gap: 8px; padding: 8px 0; border-bottom: 1px solid #334155; font-size: 0.88rem; }
    .item:last-child { border-bottom: none; }
    .dia-bloco { border: 1px solid #334155; border-radius: 10px; padding: 10px 12px; margin-bottom: 10px; background: #0f172a; }
    .dia-bloco:last-child { margin-bottom: 0; }
    .dia-topo { display: flex; justify-content: space-between; align-items: center; gap: 8px; margin-bottom: 6px; }
    .dia-titulo { font-weight: 700; color: #fb923c; font-size: 0.92rem; }
    .dia-kcal { font-size: 0.82rem; font-weight: 600; color: #e2e8f0; }
    .badge-ok { background: #14532d; color: #86efac; font-size: 0.72rem; padding: 2px 7px; border-radius: 999px; font-weight: 600; }
    .badge-warn { background: #7c2d12; color: #fed7aa; font-size: 0.72rem; padding: 2px 7px; border-radius: 999px; font-weight: 600; }
    .chart-row { margin-bottom: 12px; }
    .chart-head { display: flex; justify-content: space-between; font-size: 0.82rem; color: #e2e8f0; }
    .aba { display: none; }
    .aba.ativa { display: block; }
    nav { position: fixed; bottom: 0; left: 0; right: 0; background: #1e293b; border-top: 1px solid #334155; display: flex; justify-content: space-around; padding: 6px 2px; overflow-x: auto; }
    nav button { background: transparent; color: #94a3b8; font-size: 0.62rem; padding: 6px 2px; border-radius: 6px; min-width: 42px; }
    nav button.ativa { background: #334155; color: #fb923c; }
  </style>
</head>
<body>
  <header>
    <h1>Fire Fit</h1>
    <div class="aviso">Apoio educativo no dia a dia — não substitui profissionais de saúde.</div>
  </header>

  <main>
    <div id="alerta-banner" class="alerta-banner"></div>

    <section id="aba-painel" class="aba">
      <div class="card">
        <div id="resumo-aluno" style="font-weight:700; font-size:1rem; margin-bottom:8px;">Aluno não cadastrado</div>
        <div class="grid-2">
          <div>
            <label>Peso atual (kg)</label>
            <div class="kpi" id="kpi-peso">--</div>
          </div>
          <div>
            <label>Meta de peso (kg)</label>
            <div class="kpi" id="kpi-meta">--</div>
          </div>
        </div>
        <div class="sub" id="kpi-diff">Diferença para meta: --</div>
        <div class="sub" id="kpi-meta-kcal">Meta diária do instrutor: 1500 kcal/dia</div>
        <div class="sub" id="base-instrutor"></div>
      </div>

      <div class="card">
        <label for="p-nome">Nome</label>
        <input id="p-nome" type="text" placeholder="Nome completo" />

        <div class="grid-2">
          <div>
            <label for="p-idade">Idade</label>
            <input id="p-idade" type="number" inputmode="numeric" placeholder="Ex: 32" />
          </div>
          <div>
            <label for="p-altura">Altura (cm)</label>
            <input id="p-altura" type="number" step="0.1" inputmode="decimal" placeholder="Ex: 175" />
          </div>
        </div>

        <div class="grid-2">
          <div>
            <label for="painel-peso">Peso atual (kg)</label>
            <input id="painel-peso" type="number" step="0.1" inputmode="decimal" placeholder="Ex: 82.5" />
          </div>
          <div>
            <label for="painel-meta">Meta de peso (kg)</label>
            <input id="painel-meta" type="number" step="0.1" inputmode="decimal" placeholder="Ex: 75.0" />
          </div>
        </div>

        <div class="grid-2">
          <div>
            <label for="p-objetivo">Programa / Objetivo</label>
            <select id="p-objetivo">
              <option value="perda">Perda de peso</option>
              <option value="ganho">Ganho de massa</option>
            </select>
          </div>
          <div>
            <label for="p-meta-kcal">Meta diária de calorias (instrutor)</label>
            <input id="p-meta-kcal" type="number" step="10" inputmode="numeric" placeholder="Ex: 1500" />
          </div>
        </div>

        <button onclick="salvarPerfilCompleto()">Salvar dados e meta</button>
      </div>
    </section>

    <section id="aba-cardapio" class="aba">
      <div class="card">
        <div style="font-weight:700; font-size:1rem; margin-bottom:8px;">Cardápio da Semana por Gramas</div>
        <div class="sub" style="margin-bottom:10px;">Informe o alimento e quantas gramas pesou (ex.: 40g de feijão) que o sistema calcula as calorias automaticamente.</div>

        <label for="card-dia">Dia da semana</label>
        <select id="card-dia">
          <option value="Segunda">Segunda</option>
          <option value="Terça">Terça</option>
          <option value="Quarta">Quarta</option>
          <option value="Quinta">Quinta</option>
          <option value="Sexta">Sexta</option>
          <option value="Sábado">Sábado</option>
          <option value="Domingo">Domingo</option>
        </select>

        <label for="card-prato">Alimento / Prato</label>
        <input id="card-prato" type="text" placeholder="Ex: Feijão / Arroz branco / Peito de frango" oninput="atualizarPreviewKcal('card')" />

        <div class="grid-3">
          <div>
            <label for="card-gramas">Peso (gramas)</label>
            <input id="card-gramas" type="number" step="1" inputmode="numeric" placeholder="Ex: 40" oninput="atualizarPreviewKcal('card')" />
          </div>
          <div>
            <label for="card-kcal">Calorias (auto ou manual)</label>
            <input id="card-kcal" type="number" inputmode="numeric" placeholder="Calcula auto" />
          </div>
          <div>
            <label for="card-saude">Classificação</label>
            <select id="card-saude">
              <option value="auto">Automático</option>
              <option value="saudavel">Saudável</option>
              <option value="nao_saudavel">Não saudável</option>
            </select>
          </div>
        </div>

        <div class="calc-preview" id="card-preview">Digite o alimento e as gramas para ver as calorias calculadas.</div>
        <button type="button" onclick="adicionarPratoCardapio()">Adicionar ao cardápio da semana</button>
      </div>

      <div class="card" id="lista-cardapio-semana">
        <div class="item"><span>Nenhum prato cadastrado no cardápio da semana.</span></div>
      </div>
    </section>

    <section id="aba-calorias" class="aba">
      <div class="card">
        <div style="font-weight:700; font-size:1rem; margin-bottom:10px;">Controle Diário de Calorias (Instrutor)</div>

        <div class="grid-2">
          <div>
            <label>Precisa ingerir (meta/dia)</label>
            <div class="kpi" id="cal-aba-meta">1500 kcal</div>
          </div>
          <div>
            <label>Já ingeriu hoje</label>
            <div class="kpi" id="cal-aba-ingerido">0 kcal</div>
          </div>
        </div>

        <div class="grid-2" style="margin-top:8px;">
          <div>
            <label>Falta / Passou</label>
            <div class="kpi" id="cal-aba-saldo">Faltam 1500 kcal</div>
          </div>
          <div>
            <label>Status de saúde</label>
            <div class="kpi" id="cal-aba-saude">Aguardando</div>
          </div>
        </div>

        <div class="barra-bg"><div class="barra-fill barra-kcal" id="cal-aba-barra"></div></div>
        <div id="cal-aba-alerta" class="alerta-kcal-box faltando">Faltam 1500 kcal para atingir 1500 kcal.</div>
      </div>

      <div class="card">
        <label for="cal-aba-input-meta">Definir meta diária de calorias (instrutor)</label>
        <input id="cal-aba-input-meta" type="number" step="10" inputmode="numeric" placeholder="Ex: 1500" />

        <label for="cal-aba-input-obj">Objetivo da pessoa</label>
        <select id="cal-aba-input-obj">
          <option value="perda">Perda de peso</option>
          <option value="ganho">Ganho de massa</option>
        </select>

        <button type="button" onclick="salvarMetaCaloriasAba()">Salvar meta diária de calorias</button>
      </div>

      <div class="card">
        <label>Refeições e calorias registradas hoje</label>
        <div id="cal-aba-lista"><div class="item"><span>Nenhuma alimentação registrada hoje.</span></div></div>
      </div>
    </section>

    <section id="aba-rotina" class="aba">
      <div class="card">
        <label>Água hoje</label>
        <div class="kpi" id="agua-status">0 / 2500 ml</div>
        <div class="barra-bg"><div class="barra-fill" id="agua-barra"></div></div>
        <div class="sub" id="agua-lembrete">Lembrete de água: beba água aos poucos ao longo do dia.</div>

        <div class="grid-3" style="margin-top: 10px;">
          <button type="button" onclick="addAgua(250)">+ 250 ml</button>
          <button type="button" onclick="addAgua(500)">+ 500 ml</button>
          <button type="button" class="btn-sec" onclick="resetAgua()">Zerar dia</button>
        </div>

        <label for="agua-meta" style="margin-top: 10px;">Meta diária de água (ml)</label>
        <input id="agua-meta" type="number" step="50" inputmode="numeric" placeholder="Ex: 2500" />
        <button type="button" class="btn-sec" onclick="salvarMetaAgua()">Salvar meta de água</button>
      </div>

      <div class="card" id="lista-agua"></div>

      <div class="card">
        <label>Alerta de horário das refeições</label>
        <div class="sub" style="margin-bottom:10px;">Quando o app estiver aberto no horário configurado, ele exibe um alerta visual e notificação (se permitida).</div>
        <button type="button" class="btn-sec" style="margin-bottom:12px;" onclick="pedirPermissaoNotif()">Ativar notificações do navegador</button>

        <label for="ref-nome">Refeição</label>
        <input id="ref-nome" type="text" placeholder="Ex: Café da manhã / Pré-treino" />
        <label for="ref-hora">Horário</label>
        <input id="ref-hora" type="time" />
        <button type="button" onclick="addRefeicao()">Adicionar horário de refeição</button>
      </div>

      <div class="card" id="lista-refeicoes"></div>
    </section>

    <section id="aba-balanca" class="aba">
      <div class="card">
        <label for="bal-peso">Peso (kg)</label>
        <input id="bal-peso" type="number" step="0.1" inputmode="decimal" placeholder="Ex: 82.5" />
        <label for="bal-meta">Meta de peso (kg)</label>
        <input id="bal-meta" type="number" step="0.1" inputmode="decimal" placeholder="Ex: 75.0" />
        <button onclick="registrarBalanca()">Registrar na balança</button>
      </div>
      <div class="card" id="lista-balanca"></div>
    </section>

    <section id="aba-treinos" class="aba">
      <div class="card">
        <label>Cronômetro do treino</label>
        <div class="crono-display" id="crono-display">00:00:00</div>
        <div class="grid-3" style="margin-bottom: 10px;">
          <button type="button" onclick="iniciarCrono()">Iniciar</button>
          <button type="button" class="btn-sec" onclick="pausarCrono()">Pausar</button>
          <button type="button" class="btn-sec" onclick="zerarCrono()">Zerar</button>
        </div>
        <button type="button" class="btn-sec" onclick="usarTempoCrono()">Usar tempo no treino</button>
      </div>

      <div class="card">
        <label for="tr-desc">Treino</label>
        <input id="tr-desc" type="text" placeholder="Ex: Caminhada leve / Musculação" />
        <label for="tr-min">Duração (min)</label>
        <input id="tr-min" type="number" inputmode="numeric" placeholder="Ex: 30" />
        <button onclick="registrarTreino()">Salvar treino</button>
      </div>
      <div class="card" id="lista-treinos"></div>
    </section>

    <section id="aba-glicemia" class="aba">
      <div class="card">
        <label for="gl-val">Glicemia (mg/dL)</label>
        <input id="gl-val" type="number" step="1" inputmode="numeric" placeholder="Ex: 98" />
        <label for="gl-mom">Momento</label>
        <input id="gl-mom" type="text" placeholder="Ex: Jejum / Pós-refeição" />
        <button onclick="registrarGlicemia()">Salvar glicemia</button>
      </div>
      <div class="card" id="lista-glicemia"></div>
    </section>

    <section id="aba-alimentos" class="aba">
      <div class="card">
        <label for="al-nome">Alimento</label>
        <input id="al-nome" type="text" placeholder="Ex: Feijão / Arroz branco / Peito de frango" oninput="atualizarPreviewKcal('al')" />

        <div class="grid-3">
          <div>
            <label for="al-gramas">Peso (gramas)</label>
            <input id="al-gramas" type="number" step="1" inputmode="numeric" placeholder="Ex: 40" oninput="atualizarPreviewKcal('al')" />
          </div>
          <div>
            <label for="al-kcal">Calorias (auto ou manual)</label>
            <input id="al-kcal" type="number" inputmode="numeric" placeholder="Calcula auto" />
          </div>
          <div>
            <label for="al-saude">Tipo de alimentação</label>
            <select id="al-saude">
              <option value="auto">Automático</option>
              <option value="saudavel">Saudável</option>
              <option value="nao_saudavel">Não saudável</option>
            </select>
          </div>
        </div>

        <div class="calc-preview" id="al-preview">Digite o alimento e as gramas para ver as calorias calculadas.</div>
        <button onclick="registrarAlimento()">Salvar alimentação</button>
      </div>
      <div class="card" id="lista-alimentos"></div>
    </section>

    <section id="aba-resumo" class="aba ativa">
      <div class="card">
        <div style="display:flex; justify-content:space-between; align-items:center;">
          <span style="font-weight:700; font-size:1rem;">Dashboard do Dia</span>
          <span id="resumo-data-hoje" style="font-size:0.82rem; color:#94a3b8;">--/--/----</span>
        </div>
        <div class="sub" id="resumo-avaliacao-alim">Nenhuma alimentação registrada hoje ainda.</div>
        <div id="alerta-kcal-box" class="alerta-kcal-box faltando">Faltam 1500 kcal para atingir 1500 kcal.</div>

        <div class="grid-2" style="margin-top:12px;">
          <div>
            <label>Água tomada hoje</label>
            <div class="kpi" id="dash-agua">0 / 2500 ml</div>
          </div>
          <div>
            <label>Calorias / Meta do instrutor</label>
            <div class="kpi" id="dash-kcal">0 / 1500 kcal</div>
          </div>
          <div>
            <label>Tempo de treino hoje</label>
            <div class="kpi" id="dash-treino">0 min</div>
          </div>
          <div>
            <label>Registros de destros hoje</label>
            <div class="kpi" id="dash-destros">0</div>
          </div>
        </div>
      </div>

      <div class="card">
        <label>Gráfico comparativo do dia</label>

        <div class="chart-row">
          <div class="chart-head">
            <span>Hidratação (meta diária)</span>
            <span id="grafico-agua-txt">0% (0 ml)</span>
          </div>
          <div class="barra-bg"><div class="barra-fill" id="grafico-agua-bar"></div></div>
        </div>

        <div class="chart-row">
          <div class="chart-head">
            <span>Proporção de itens saudáveis</span>
            <span id="grafico-saude-txt">Sem registros hoje</span>
          </div>
          <div class="barra-bg"><div class="barra-fill barra-saude" id="grafico-saude-bar"></div></div>
        </div>

        <div class="chart-row">
          <div class="chart-head">
            <span id="grafico-kcal-label">Calorias do dia (meta 1.500 kcal)</span>
            <span id="grafico-kcal-txt">0 / 1500 kcal (0%)</span>
          </div>
          <div class="barra-bg"><div class="barra-fill barra-kcal" id="grafico-kcal-bar"></div></div>
        </div>

        <div class="chart-row">
          <div class="chart-head">
            <span>Tempo de treino hoje (ref. 45 min)</span>
            <span id="grafico-treino-txt">0 min (0%)</span>
          </div>
          <div class="barra-bg"><div class="barra-fill barra-treino" id="grafico-treino-bar"></div></div>
        </div>
      </div>

      <div class="card">
        <label>O que você comeu hoje (e classificação)</label>
        <div id="dash-lista-prato"><div class="item"><span>Nenhuma alimentação registrada hoje.</span></div></div>
      </div>

      <div class="card">
        <label>Água, treinos e destros registrados hoje</label>
        <div id="dash-lista-atividades"><div class="item"><span>Nenhuma atividade registrada hoje ainda.</span></div></div>
      </div>
    </section>
  </main>

  <nav>
    <button onclick="abrirAba('painel', this)">Painel</button>
    <button onclick="abrirAba('cardapio', this)">Cardápio</button>
    <button onclick="abrirAba('calorias', this)">Calorias</button>
    <button onclick="abrirAba('rotina', this)">Água/Ref.</button>
    <button onclick="abrirAba('balanca', this)">Balança</button>
    <button onclick="abrirAba('treinos', this)">Treinos</button>
    <button onclick="abrirAba('glicemia', this)">Glicemia</button>
    <button onclick="abrirAba('alimentos', this)">Alim.</button>
    <button class="ativa" onclick="abrirAba('resumo', this)">Resumo</button>
  </nav>

  <script>
    const DIAS_ORDEM = ["Segunda", "Terça", "Quarta", "Quinta", "Sexta", "Sábado", "Domingo"];
    let tabelaKcal100g = {
      "arroz branco": 128,
      "arroz": 128,
      "arroz integral": 124,
      "feijao": 76,
      "feijão": 76,
      "peito de frango": 159,
      "frango": 159,
      "patinho": 219,
      "carne magra": 180,
      "batata doce": 77,
      "batata-doce": 77,
      "batata": 52,
      "ovo": 146,
      "ovos": 146,
      "aveia": 394,
      "banana": 89
    };

    let cronoSegundos = 0;
    let cronoTimer = null;
    let ultimoEstado = null;
    const alertasDisparadosHoje = new Set();

    function estimarKcal100g(nome) {
      const texto = (nome || "").toLowerCase();
      const chaves = Object.keys(tabelaKcal100g || {}).sort((a, b) => b.length - a.length);
      for (const ch of chaves) {
        if (texto.includes(ch)) return tabelaKcal100g[ch];
      }
      return null;
    }

    function atualizarPreviewKcal(prefixo) {
      const nome = document.getElementById(`${prefixo}-prato`)
        ? document.getElementById(`${prefixo}-prato`).value
        : document.getElementById(`${prefixo}-nome`).value;
      const gramasVal = parseFloat(document.getElementById(`${prefixo}-gramas`).value);
      const kcalInput = document.getElementById(`${prefixo}-kcal`);
      const preview = document.getElementById(`${prefixo}-preview`);
      const base100 = estimarKcal100g(nome);

      if (base100 !== null && !isNaN(gramasVal) && gramasVal > 0) {
        const calc = Math.round((gramasVal / 100) * base100);
        kcalInput.value = calc;
        preview.textContent = `${gramasVal}g de ${nome.trim()} = ${calc} kcal (${base100} kcal/100g).`;
      } else if (base100 !== null) {
        preview.textContent = `${nome.trim()} tem referência de ${base100} kcal por 100g. Digite as gramas para calcular.`;
      } else {
        preview.textContent = 'Alimento fora da tabela base: você pode informar as calorias manualmente.';
      }
    }

    function formatarCrono(seg) {
      const h = String(Math.floor(seg / 3600)).padStart(2, '0');
      const m = String(Math.floor((seg % 3600) / 60)).padStart(2, '0');







cd C:\Users\Eduardo\fire_fit

@'
import json
import os
from datetime import datetime
from zoneinfo import ZoneInfo
from flask import Flask, jsonify, render_template, request

try:
    import psycopg2
except ImportError:
    psycopg2 = None

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE_DIR, "dados_fire_fit.json")
DATABASE_URL = os.environ.get("DATABASE_URL", "").strip()
TZ_BR = ZoneInfo("America/Sao_Paulo")

app = Flask(__name__, template_folder=BASE_DIR)

DIAS_SEMANA = [
    "Segunda",
    "Terça",
    "Quarta",
    "Quinta",
    "Sexta",
    "Sábado",
    "Domingo"
]

DEFAULT_REFEICOES = [
    {"nome": "Café da manhã", "horario": "08:00"},
    {"nome": "Almoço", "horario": "12:30"},
    {"nome": "Lanche da tarde", "horario": "16:00"},
    {"nome": "Jantar", "horario": "19:30"}
]

TABELA_KCAL_100G = {
    "arroz branco": 128,
    "arroz": 128,
    "arroz integral": 124,
    "feijao": 76,
    "feijão": 76,
    "feijao carioca": 76,
    "feijão carioca": 76,
    "feijao preto": 77,
    "feijão preto": 77,
    "lentilha": 93,
    "grao de bico": 164,
    "grão de bico": 164,
    "ervilha": 81,
    "batata doce": 77,
    "batata-doce": 77,
    "batata inglesa": 52,
    "batata": 52,
    "mandioca": 125,
    "aipim": 125,
    "macaxeira": 125,
    "inhame": 97,
    "cara": 97,
    "cará": 97,
    "cuscuz": 113,
    "aveia": 394,
    "granola": 430,
    "macarrao": 102,
    "macarrão": 102,
    "macarrao integral": 124,
    "macarrão integral": 124,
    "pao frances": 300,
    "pão francês": 300,
    "pao de forma": 265,
    "pão de forma": 265,
    "pao integral": 253,
    "pão integral": 253,
    "tapioca": 240,
    "peito de frango": 159,
    "frango": 159,
    "coxa de frango": 215,
    "sobrecoxa": 232,
    "bife": 219,
    "patinho": 219,
    "alcatra": 241,
    "contrafile": 266,
    "contrafilé": 266,
    "acem": 215,
    "acém": 215,
    "carne moida": 212,
    "carne moída": 212,
    "carne magra": 180,
    "lombo suino": 197,
    "lombo suíno": 197,
    "tilapia": 96,
    "tilápia": 96,
    "atum": 116,
    "sardinha": 185,
    "salmao": 211,
    "salmão": 211,
    "merluza": 89,
    "camarao": 90,
    "camarão": 90,
    "ovo": 146,
    "ovos": 146,
    "clara de ovo": 52,
    "leite integral": 61,
    "leite desnatado": 35,
    "leite semidesnatado": 46,
    "iogurte natural": 51,
    "iogurte grego": 115,
    "queijo minas": 264,
    "queijo cottage": 98,
    "queijo mucarela": 300,
    "queijo muçarela": 300,
    "queijo prato": 360,
    "requeijao": 257,
    "requeijão": 257,
    "requeijao light": 181,
    "requeijão light": 181,
    "banana": 89,
    "banana prata": 87,
    "banana nanica": 92,
    "maca": 56,
    "maçã": 56,
    "mamao": 40,
    "mamão": 40,
    "melancia": 33,
    "melao": 29,
    "melão": 29,
    "morango": 30,
    "abacaxi": 48,
    "laranja": 46,
    "uva": 53,
    "manga": 64,
    "pera": 53,
    "pêra": 53,
    "goiaba": 68,
    "abacate": 96,
    "kiwi": 51,
    "brocolis": 25,
    "brócolis": 25,
    "couve": 27,
    "alface": 14,
    "tomate": 15,
    "pepino": 10,
    "cenoura": 34,
    "abobrinha": 19,
    "berinjela": 19,
    "chuchu": 19,
    "vagem": 25,
    "espinafre": 16,
    "palmito": 23,
    "castanha de caju": 570,
    "castanha do para": 643,
    "castanha do pará": 643,
    "amendoim": 544,
    "amendoa": 581,
    "amêndoa": 581,
    "chia": 486,
    "linhaca": 495,
    "linhaça": 495,
    "peito de peru": 108,
    "presunto": 165,
    "bacon": 541,
    "linguica": 296,
    "linguiça": 296,
    "salsicha": 246,
    "pizza": 266,
    "hamburguer": 295,
    "hambúrguer": 295,
    "coxinha": 263,
    "pastel": 310,
    "batata frita": 312,
    "chocolate": 535,
    "sorvete": 207,
    "bolo": 350,
    "biscoito": 440,
    "bolacha": 440,
    "pao de queijo": 363,
    "pão de queijo": 363
}

DEFAULT_DATA = {
    "perfil": {
        "nome": "",
        "idade": None,
        "altura_cm": None,
        "objetivo": "perda"
    },
    "meta_peso": 75.0,
    "peso_atual": None,
    "meta_kcal_dia": 1500,
    "agua": {
        "meta_ml": 2500,
        "consumido_ml": 0,
        "data_ref": "",
        "historico": []
    },
    "refeicoes": DEFAULT_REFEICOES,
    "cardapio_semana": [],
    "balanca": [],
    "treinos": [],
    "glicemia": [],
    "alimentos": []
}

PALAVRAS_SAUDAVEIS = [
    "arroz integral", "frango", "peito de frango", "coxa de frango", "sobrecoxa",
    "bife", "patinho", "alcatra", "contrafile", "contrafilé", "acem", "acém",
    "carne moida", "carne moída", "carne magra", "lombo suino", "lombo suíno",
    "ovo", "ovos", "clara de ovo", "banana", "fruta", "frutas", "salada",
    "legume", "legumes", "brocolis", "brócolis", "couve", "alface", "tomate",
    "pepino", "cenoura", "abobrinha", "berinjela", "chuchu", "vagem", "espinafre",
    "palmito", "aveia", "peixe", "tilapia", "tilápia", "atum", "sardinha",
    "merluza", "camarao", "camarão", "batata doce", "batata-doce", "feijao", "feijão",
    "lentilha", "grao de bico", "grão de bico", "ervilha", "iogurte natural",
    "iogurte grego", "queijo minas", "queijo cottage", "leite desnatado",
    "leite semidesnatado", "castanha", "amendoim", "amendoa", "amêndoa",
    "chia", "linhaca", "linhaça", "abacate", "morango", "maca", "maçã",
    "mamao", "mamão", "melancia", "melao", "melão", "abacaxi", "laranja",
    "uva", "manga", "pera", "pêra", "goiaba", "kiwi", "whey", "salmao",
    "salmão", "cuscuz", "mandioca", "aipim", "macaxeira", "inhame", "cara",
    "cará", "peito de peru", "tapioca"
]

PALAVRAS_NAO_SAUDAVEIS = [
    "fritura", "frito", "frita", "batata frita", "doce", "chocolate", "sorvete",
    "refrigerante", "refri", "pizza", "hamburguer", "hambúrguer", "burger",
    "salgado", "coxinha", "pastel", "empada", "biscoito", "bolacha", "bolo",
    "pudim", "cerveja", "alcool", "álcool", "fast food", "bacon", "linguica",
    "linguiça", "salsicha", "presunto", "maionese", "chantilly", "leite condensado"
]


def buscar_kcal_por_100g(nome_alimento):
    texto = (nome_alimento or "").lower()
    for chave in sorted(TABELA_KCAL_100G.keys(), key=len, reverse=True):
        if chave in texto:
            return TABELA_KCAL_100G[chave]
    return None


def calcular_kcal_por_gramas(nome_alimento, gramas, kcal_manual=None):
    kcal_100g = buscar_kcal_por_100g(nome_alimento)
    try:
        g = float(gramas) if gramas not in (None, "") else 0.0
    except Exception:
        g = 0.0

    if kcal_manual not in (None, ""):
        try:
            manual_val = max(0, int(round(float(kcal_manual))))
            if kcal_100g is not None and g > 0:
                auto_val = int(round((g / 100.0) * kcal_100g))
                return manual_val if manual_val != auto_val else auto_val
            return manual_val
        except Exception:
            pass

    if kcal_100g is not None and g > 0:
        return int(round((g / 100.0) * kcal_100g))

    if kcal_100g is not None:
        return int(kcal_100g)

    return 0


def classificar_saude(item_nome, tipo_informado=None):
    if tipo_informado in ("saudavel", "nao_saudavel"):
        return tipo_informado == "saudavel"
    texto = (item_nome or "").lower()
    for p in PALAVRAS_NAO_SAUDAVEIS:
        if p in texto:
            return False
    for p in PALAVRAS_SAUDAVEIS:
        if p in texto:
            return True
    return True


def agora_br_dt():
    return datetime.now(TZ_BR)


def agora_br():
    return agora_br_dt().strftime("%d/%m %H:%M")


def hoje_br():
    return agora_br_dt().strftime("%Y-%m-%d")


def hoje_br_curto():
    return agora_br_dt().strftime("%d/%m")


def avaliar_calorias_dia(kcal_consumidas, meta_kcal, objetivo="perda", qtd_nao_saudaveis=0):
    consumido = int(kcal_consumidas or 0)
    meta = max(1, int(meta_kcal or 1500))
    diff = consumido - meta
    foco_txt = "ganho de massa" if objetivo == "ganho" else "perda de peso"

    if diff > 0:
        passou = diff
        saude_txt = "Não está saudável / passou da meta"
        return {
            "status": "passou",
            "diferenca": diff,
            "faltam": 0,
            "passou": passou,
            "saude_status": "nao_saudavel",
            "saude_texto": saude_txt,
            "mensagem": f"Já consumiu {consumido} kcal e passou {passou} kcal da meta de {meta} kcal ({foco_txt}). {saude_txt}!"
        }

    if diff < 0:
        faltam = abs(diff)
        saude_txt = "Atenção: há item não saudável hoje" if qtd_nao_saudaveis > 0 else ("Saudável até o momento" if consumido > 0 else "Aguardando registro")
        return {
            "status": "faltando",
            "diferenca": diff,
            "faltam": faltam,
            "passou": 0,
            "saude_status": "nao_saudavel" if qtd_nao_saudaveis > 0 else "saudavel",
            "saude_texto": saude_txt,
            "mensagem": f"Já consumiu {consumido} kcal de {meta} kcal — faltam {faltam} kcal ({foco_txt})."
        }

    saude_txt = "Atenção: há item não saudável hoje" if qtd_nao_saudaveis > 0 else "Dentro da meta e saudável"
    return {
        "status": "na_meta",
        "diferenca": 0,
        "faltam": 0,
        "passou": 0,
        "saude_status": "nao_saudavel" if qtd_nao_saudaveis > 0 else "saudavel",
        "saude_texto": saude_txt,
        "mensagem": f"Já consumiu {consumido} kcal e atingiu a meta de {meta} kcal ({foco_txt})."
    }


def normalizar_dados(raw):
    data = json.loads(json.dumps(DEFAULT_DATA))
    if isinstance(raw, dict):
        for k, v in DEFAULT_DATA.items():
            if k in raw and raw[k] is not None:
                data[k] = raw[k]
        if isinstance(raw.get("perfil"), dict):
            for pk, pv in DEFAULT_DATA["perfil"].items():
                if pk in raw["perfil"]:
                    data["perfil"][pk] = raw["perfil"][pk]
        if isinstance(raw.get("agua"), dict):
            for ak, av in DEFAULT_DATA["agua"].items():
                if ak in raw["agua"]:
                    data["agua"][ak] = raw["agua"][ak]
        if not isinstance(data.get("refeicoes"), list) or not data["refeicoes"]:
            data["refeicoes"] = json.loads(json.dumps(DEFAULT_REFEICOES))
        if not isinstance(data.get("cardapio_semana"), list):
            data["cardapio_semana"] = []

    try:
        data["meta_kcal_dia"] = max(200, int(data.get("meta_kcal_dia") or 1500))
    except Exception:
        data["meta_kcal_dia"] = 1500

    hoje = hoje_br()
    if data["agua"].get("data_ref") and data["agua"].get("data_ref") != hoje:
        data["agua"]["consumido_ml"] = 0
        data["agua"]["historico"] = []
    data["agua"]["data_ref"] = hoje

    for item in data.get("alimentos", []):
        if "saudavel" not in item:
            item["saudavel"] = classificar_saude(item.get("nome", ""))
        if "data" not in item:
            item["data"] = ""
        if "gramas" not in item:
            item["gramas"] = None

    for prato in data.get("cardapio_semana", []):
        dia = prato.get("dia", "Segunda")
        if dia not in DIAS_SEMANA:
            prato["dia"] = "Segunda"
        if not prato.get("refeicao"):
            prato["refeicao"] = "Almoço"
        porcoes = prato.get("porcoes")
        if not isinstance(porcoes, list):
            porcoes = []
            if prato.get("prato"):
                porcoes.append({
                    "alimento": prato.get("prato"),
                    "gramas": prato.get("gramas"),
                    "kcal": int(prato.get("kcal", 0) or 0),
                    "saudavel": prato.get("saudavel", True)
                })
        for p in porcoes:
            p["kcal"] = int(p.get("kcal", 0) or 0)
            if "saudavel" not in p:
                p["saudavel"] = classificar_saude(p.get("alimento", ""))
        prato["porcoes"] = porcoes
        prato["total_kcal"] = sum(int(p.get("kcal", 0) or 0) for p in porcoes)

    return data


def _pg_conn():
    if not DATABASE_URL or psycopg2 is None:
        return None
    sslmode = "disable" if ("localhost" in DATABASE_URL or "127.0.0.1" in DATABASE_URL) else "require"
    return psycopg2.connect(DATABASE_URL, sslmode=sslmode)


def _garantir_tabela_pg(conn):
    with conn.cursor() as cur:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS fire_fit_estado (
                id INTEGER PRIMARY KEY,
                payload JSONB NOT NULL,
                atualizado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        cur.execute("SELECT payload FROM fire_fit_estado WHERE id = 1")
        row = cur.fetchone()
        if row is None:
            cur.execute(
                "INSERT INTO fire_fit_estado (id, payload) VALUES (1, %s::jsonb)",
                (json.dumps(DEFAULT_DATA, ensure_ascii=False),)
            )
    conn.commit()


def load_data():
    if DATABASE_URL:
        conn = _pg_conn()
        if conn is not None:
            try:
                _garantir_tabela_pg(conn)
                with conn.cursor() as cur:
                    cur.execute("SELECT payload FROM fire_fit_estado WHERE id = 1")
                    row = cur.fetchone()
                if row and row[0] is not None:
                    return normalizar_dados(row[0])
                return normalizar_dados(DEFAULT_DATA)
            finally:
                conn.close()

    if not os.path.exists(DATA_FILE):
        save_data(DEFAULT_DATA)
        return normalizar_dados(DEFAULT_DATA)
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            raw = json.load(f)
        return normalizar_dados(raw)
    except Exception:
        return normalizar_dados(DEFAULT_DATA)


def save_data(data):
    limpo = normalizar_dados(data)
    if DATABASE_URL:
        conn = _pg_conn()
        if conn is not None:
            try:
                _garantir_tabela_pg(conn)
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        INSERT INTO fire_fit_estado (id, payload, atualizado_em)
                        VALUES (1, %s::jsonb, CURRENT_TIMESTAMP)
                        ON CONFLICT (id) DO UPDATE
                        SET payload = EXCLUDED.payload, atualizado_em = CURRENT_TIMESTAMP
                        """,
                        (json.dumps(limpo, ensure_ascii=False),)
                    )
                conn.commit()
                return
            finally:
                conn.close()

    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(limpo, f, ensure_ascii=False, indent=2)


def orientacao_instrutor(perfil, peso, meta, meta_kcal):
    objetivo = (perfil or {}).get("objetivo", "perda")
    diff = round(peso - meta, 1) if (peso is not None and meta is not None) else None

    if objetivo == "ganho":
        foco = "Ganho de massa"
        base = f"Meta diária definida pelo instrutor: {meta_kcal} kcal/dia para ganho de massa."
        if diff is not None:
            if diff < 0:
                meta_txt = f"Faltam {abs(diff)} kg para atingir a meta de ganho."
            elif diff > 0:
                meta_txt = f"Está {diff} kg acima da meta definida."
            else:
                meta_txt = "Meta de peso atingida."
        else:
            meta_txt = "Informe peso atual e meta para acompanhar a distância."
    else:
        foco = "Perda de peso"
        base = f"Meta diária definida pelo instrutor: {meta_kcal} kcal/dia para perda de peso."
        if diff is not None:
            if diff > 0:
                meta_txt = f"Restam {diff} kg para chegar à meta de peso."
            elif diff < 0:
                meta_txt = f"Está {abs(diff)} kg abaixo da meta definida."
            else:
                meta_txt = "Meta de peso atingida."
        else:
            meta_txt = "Informe peso atual e meta para acompanhar a distância."

    return {
        "foco": foco,
        "meta_status": meta_txt,
        "base_resumo": base
    }


def montar_resumo_dia(data):
    prefixo_hoje = hoje_br_curto() + " "

    alimentos_hoje = [x for x in data.get("alimentos", []) if str(x.get("data", "")).startswith(prefixo_hoje)]
    treinos_hoje = [x for x in data.get("treinos", []) if str(x.get("data", "")).startswith(prefixo_hoje)]
    balanca_hoje = [x for x in data.get("balanca", []) if str(x.get("data", "")).startswith(prefixo_hoje)]
    glicemia_hoje = [x for x in data.get("glicemia", []) if str(x.get("data", "")).startswith(prefixo_hoje)]
    agua = data.get("agua", DEFAULT_DATA["agua"])
    objetivo = (data.get("perfil") or {}).get("objetivo", "perda")

    kcal_total = sum(int(x.get("kcal", 0) or 0) for x in alimentos_hoje)
    qtd_saudaveis = sum(1 for x in alimentos_hoje if x.get("saudavel", True))
    qtd_nao_saudaveis = sum(1 for x in alimentos_hoje if not x.get("saudavel", True))

    meta_kcal = int(data.get("meta_kcal_dia") or 1500)
    alerta_kcal = avaliar_calorias_dia(kcal_total, meta_kcal, objetivo, qtd_nao_saudaveis)

    if not alimentos_hoje:
        avaliacao_alimentacao = "Nenhuma alimentação registrada hoje ainda."
    elif qtd_nao_saudaveis == 0:
        avaliacao_alimentacao = "Alimentação do dia dentro do saudável."
    elif qtd_saudaveis >= qtd_nao_saudaveis:
        avaliacao_alimentacao = f"Predomínio saudável ({qtd_saudaveis} saudáveis vs. {qtd_nao_saudaveis} fora do padrão)."
    else:
        avaliacao_alimentacao = f"Atenção: mais itens fora do saudável hoje ({qtd_nao_saudaveis} vs. {qtd_saudaveis} saudáveis)."

    minutos_treino_hoje = sum(int(x.get("minutos", 0) or 0) for x in treinos_hoje)
    destros_hoje = len(balanca_hoje)

    return {
        "data_hoje": agora_br_dt().strftime("%d/%m/%Y"),
        "objetivo": objetivo,
        "agua_ml": int(agua.get("consumido_ml", 0) or 0),
        "meta_agua_ml": int(agua.get("meta_ml", 2500) or 2500),
        "agua_historico": agua.get("historico", []),
        "kcal_hoje": kcal_total,
        "meta_kcal_dia": meta_kcal,
        "alerta_kcal": alerta_kcal,
        "qtd_saudaveis": qtd_saudaveis,
        "qtd_nao_saudaveis": qtd_nao_saudaveis,
        "avaliacao_alimentacao": avaliacao_alimentacao,
        "alimentos_hoje": alimentos_hoje,
        "minutos_treino_hoje": minutos_treino_hoje,
        "treinos_hoje": treinos_hoje,
        "destros_hoje": destros_hoje,
        "balanca_hoje": balanca_hoje,
        "glicemia_hoje": glicemia_hoje
    }


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/estado", methods=["GET"])
def get_estado():
    data = load_data()
    peso = data.get("peso_atual")
    meta = data.get("meta_peso")
    perfil = data.get("perfil", {})
    meta_kcal = int(data.get("meta_kcal_dia") or 1500)
    diferenca = round(peso - meta, 1) if (peso is not None and meta is not None) else None
    return jsonify({
        "hora_servidor_br": agora_br_dt().strftime("%H:%M"),
        "perfil": perfil,
        "peso_atual": peso,
        "meta_peso": meta,
        "meta_kcal_dia": meta_kcal,
        "diferenca_meta": diferenca,
        "orientacao": orientacao_instrutor(perfil, peso, meta, meta_kcal),
        "tabela_kcal_100g": TABELA_KCAL_100G,
        "agua": data.get("agua", DEFAULT_DATA["agua"]),
        "refeicoes": data.get("refeicoes", DEFAULT_REFEICOES),
        "cardapio_semana": data.get("cardapio_semana", []),
        "balanca": data.get("balanca", []),
        "treinos": data.get("treinos", []),
        "glicemia": data.get("glicemia", []),
        "alimentos": data.get("alimentos", []),
        "resumo_dia": montar_resumo_dia(data)
    })


@app.route("/api/cardapio/prato", methods=["POST"])
def salvar_prato_cardapio():
    payload = request.get_json(force=True) or {}
    data = load_data()
    dia = str(payload.get("dia", "Segunda")).strip()
    if dia not in DIAS_SEMANA:
        dia = "Segunda"
    refeicao = str(payload.get("refeicao", "Almoço")).strip() or "Almoço"
    porcoes_raw = payload.get("porcoes") or []
    porcoes = []
    for p in porcoes_raw:
        alimento = str(p.get("alimento", "")).strip()
        if not alimento:
            continue
        gramas_raw = p.get("gramas")
        gramas = int(round(float(gramas_raw))) if gramas_raw not in (None, "") else None
        kcal = calcular_kcal_por_gramas(alimento, gramas_raw, p.get("kcal"))
        saudavel = classificar_saude(alimento, p.get("saude_tipo"))
        porcoes.append({
            "alimento": alimento,
            "gramas": gramas,
            "kcal": kcal,
            "saudavel": saudavel
        })

    if not porcoes:
        return jsonify({"ok": False, "erro": "Adicione ao menos uma porção ao prato."}), 400

    total_kcal = sum(int(x.get("kcal", 0) or 0) for x in porcoes)
    data.setdefault("cardapio_semana", []).append({
        "dia": dia,
        "refeicao": refeicao,
        "porcoes": porcoes,
        "total_kcal": total_kcal
    })
    save_data(data)
    return jsonify({"ok": True, "total_kcal": total_kcal})


@app.route("/api/cardapio/excluir/<int:idx>", methods=["DELETE"])
def excluir_cardapio(idx):
    data = load_data()
    lista = data.get("cardapio_semana", [])
    if 0 <= idx < len(lista):
        lista.pop(idx)
        data["cardapio_semana"] = lista
        save_data(data)
    return jsonify({"ok": True})


@app.route("/api/cardapio/consumir/<int:idx>", methods=["POST"])
def consumir_cardapio(idx):
    data = load_data()
    lista = data.get("cardapio_semana", [])
    if 0 <= idx < len(lista):
        prato = lista[idx]
        refeicao = str(prato.get("refeicao", "Refeição")).strip()
        porcoes = prato.get("porcoes") or []
        for p in porcoes:
            alimento_nome = str(p.get("alimento", "")).strip()
            rotulo = f"{refeicao}: {alimento_nome}" if refeicao else alimento_nome
            data.setdefault("alimentos", []).insert(0, {
                "data": agora_br(),
                "nome": rotulo,
                "gramas": p.get("gramas"),
                "kcal": int(p.get("kcal", 0) or 0),
                "saudavel": bool(p.get("saudavel", True))
            })
        save_data(data)
    return jsonify({"ok": True})


@app.route("/api/agua", methods=["POST"])
def atualizar_agua():
    payload = request.get_json(force=True) or {}
    data = load_data()
    agua = data.get("agua", json.loads(json.dumps(DEFAULT_DATA["agua"])))

    if "meta_ml" in payload and payload["meta_ml"] not in (None, ""):
        agua["meta_ml"] = max(250, int(payload["meta_ml"]))

    if payload.get("resetar"):
        agua["consumido_ml"] = 0
        agua["historico"] = []
    elif "add_ml" in payload and payload["add_ml"] not in (None, ""):
        add_val = int(payload["add_ml"])
        agua["consumido_ml"] = max(0, int(agua.get("consumido_ml", 0)) + add_val)
        agua.setdefault("historico", []).insert(0, {
            "hora": agora_br_dt().strftime("%H:%M"),
            "ml": add_val
        })

    agua["data_ref"] = hoje_br()
    data["agua"] = agua
    save_data(data)
    return jsonify({"ok": True})


@app.route("/api/agua/excluir/<int:idx>", methods=["DELETE"])
def excluir_agua(idx):
    data = load_data()
    agua = data.get("agua", json.loads(json.dumps(DEFAULT_DATA["agua"])))
    hist = agua.get("historico", [])
    if 0 <= idx < len(hist):
        removido = hist.pop(idx)
        agua["consumido_ml"] = max(0, int(agua.get("consumido_ml", 0)) - int(removido.get("ml", 0)))
        agua["historico"] = hist
        data["agua"] = agua
        save_data(data)
    return jsonify({"ok": True})


@app.route("/api/refeicoes", methods=["POST"])
def add_refeicao():
    payload = request.get_json(force=True) or {}
    data = load_data()
    nome = str(payload.get("nome", "")).strip() or "Refeição"
    horario = str(payload.get("horario", "12:00")).strip() or "12:00"
    data.setdefault("refeicoes", []).append({"nome": nome, "horario": horario})
    data["refeicoes"].sort(key=lambda x: x.get("horario", ""))
    save_data(data)
    return jsonify({"ok": True})


@app.route("/api/refeicoes/excluir/<int:idx>", methods=["DELETE"])
def excluir_refeicao(idx):
    data = load_data()
    lista = data.get("refeicoes", [])
    if 0 <= idx < len(lista):
        lista.pop(idx)
        data["refeicoes"] = lista
        save_data(data)
    return jsonify({"ok": True})


@app.route("/api/perfil", methods=["POST"])
def salvar_perfil():
    payload = request.get_json(force=True) or {}
    data = load_data()
    perfil = data.get("perfil", {})

    if "nome" in payload:
        perfil["nome"] = str(payload.get("nome", "")).strip()

    if "idade" in payload:
        val = payload.get("idade")
        perfil["idade"] = int(val) if val not in (None, "") else None

    if "altura_cm" in payload:
        val = payload.get("altura_cm")
        perfil["altura_cm"] = float(val) if val not in (None, "") else None

    if "objetivo" in payload and payload.get("objetivo") in ("perda", "ganho"):
        perfil["objetivo"] = payload.get("objetivo")

    if "meta_kcal_dia" in payload and payload["meta_kcal_dia"] not in (None, ""):
        data["meta_kcal_dia"] = max(200, int(payload["meta_kcal_dia"]))

    if "meta_peso" in payload and payload["meta_peso"] not in (None, ""):
        data["meta_peso"] = float(payload["meta_peso"])

    if "peso_atual" in payload and payload["peso_atual"] not in (None, ""):
        peso_val = float(payload["peso_atual"])
        data["peso_atual"] = peso_val
        data["balanca"].insert(0, {
            "data": agora_br(),
            "peso": peso_val,
            "meta": data["meta_peso"]
        })

    data["perfil"] = perfil
    save_data(data)
    return jsonify({"ok": True})


@app.route("/api/balanca", methods=["POST"])
def add_balanca():
    payload = request.get_json(force=True) or {}
    data = load_data()
    peso_val = float(payload.get("peso", 0) or 0)
    if payload.get("meta_peso") not in (None, ""):
        data["meta_peso"] = float(payload["meta_peso"])
    data["peso_atual"] = peso_val
    data["balanca"].insert(0, {
        "data": agora_br(),
        "peso": peso_val,
        "meta": data["meta_peso"]
    })
    save_data(data)
    return jsonify({"ok": True})


@app.route("/api/treinos", methods=["POST"])
def add_treino():
    payload = request.get_json(force=True) or {}
    data = load_data()
    data["treinos"].insert(0, {
        "data": agora_br(),
        "descricao": str(payload.get("descricao", "")).strip(),
        "minutos": int(payload.get("minutos", 0) or 0),
        "tempo_fmt": str(payload.get("tempo_fmt", "")).strip()
    })
    save_data(data)
    return jsonify({"ok": True})


@app.route("/api/glicemia", methods=["POST"])
def add_glicemia():
    payload = request.get_json(force=True) or {}
    data = load_data()
    data["glicemia"].insert(0, {
        "data": agora_br(),
        "valor": float(payload.get("valor", 0) or 0),
        "momento": str(payload.get("momento", "Registro")).strip()
    })
    save_data(data)
    return jsonify({"ok": True})


@app.route("/api/alimentos", methods=["POST"])
def add_alimento():
    payload = request.get_json(force=True) or {}
    data = load_data()
    nome_alimento = str(payload.get("nome", "")).strip()
    gramas_raw = payload.get("gramas")
    gramas = int(round(float(gramas_raw))) if gramas_raw not in (None, "") else None
    kcal = calcular_kcal_por_gramas(nome_alimento, gramas_raw, payload.get("kcal"))
    data["alimentos"].insert(0, {
        "data": agora_br(),
        "nome": nome_alimento,
        "gramas": gramas,
        "kcal": kcal,
        "saudavel": classificar_saude(nome_alimento, payload.get("saude_tipo"))
    })
    save_data(data)
    return jsonify({"ok": True, "kcal": kcal})


@app.route("/api/excluir/<categoria>/<int:idx>", methods=["DELETE"])
def excluir_item(categoria, idx):
    permitidos = {"balanca", "treinos", "glicemia", "alimentos"}
    if categoria not in permitidos:
        return jsonify({"ok": False, "erro": "Categoria inválida"}), 400
    data = load_data()
    lista = data.get(categoria, [])
    if 0 <= idx < len(lista):
        lista.pop(idx)
        data[categoria] = lista
        if categoria == "balanca":
            data["peso_atual"] = lista[0]["peso"] if lista else None
        save_data(data)
    return jsonify({"ok": True})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
