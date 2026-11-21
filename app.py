import json
import os
import sqlite3
import uuid
from datetime import datetime, timedelta
from flask import Flask, jsonify, render_template, request

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ARQUIVO_JSON_LEGADO = os.path.join(BASE_DIR, "dados_fire_fit.json")
DATABASE_PATH = os.environ.get("DATABASE_PATH", os.path.join(BASE_DIR, "fire_fit.db"))
DATABASE_URL = os.environ.get("DATABASE_URL", "").strip()

ALIMENTOS_INICIAIS = [
    {"id": "ali-1", "nome": "Arroz branco cozido", "estado": "Cozido", "kcal_100g": 128.0, "carb_100g": 28.1, "prot_100g": 2.5, "gord_100g": 0.2, "favorito": True},
    {"id": "ali-2", "nome": "Feijão carioca cozido", "estado": "Cozido", "kcal_100g": 76.0, "carb_100g": 13.6, "prot_100g": 4.8, "gord_100g": 0.5, "favorito": True},
    {"id": "ali-3", "nome": "Peito de frango grelhado", "estado": "Grelhado", "kcal_100g": 159.0, "carb_100g": 0.0, "prot_100g": 32.0, "gord_100g": 2.5, "favorito": True},
    {"id": "ali-4", "nome": "Batata inglesa cozida", "estado": "Cozido", "kcal_100g": 52.0, "carb_100g": 11.9, "prot_100g": 1.2, "gord_100g": 0.1, "favorito": False},
    {"id": "ali-5", "nome": "Batata-doce cozida", "estado": "Cozido", "kcal_100g": 77.0, "carb_100g": 18.4, "prot_100g": 0.6, "gord_100g": 0.1, "favorito": True},
    {"id": "ali-6", "nome": "Pão francês", "estado": "Pronto", "kcal_100g": 300.0, "carb_100g": 58.6, "prot_100g": 8.0, "gord_100g": 3.1, "favorito": True},
    {"id": "ali-7", "nome": "Ovo inteiro cozido", "estado": "Cozido", "kcal_100g": 146.0, "carb_100g": 0.6, "prot_100g": 13.3, "gord_100g": 9.5, "favorito": True},
    {"id": "ali-8", "nome": "Banana nanica", "estado": "In natura", "kcal_100g": 92.0, "carb_100g": 23.8, "prot_100g": 1.4, "gord_100g": 0.1, "favorito": False},
    {"id": "ali-9", "nome": "Aveia em flocos", "estado": "Seco", "kcal_100g": 394.0, "carb_100g": 66.6, "prot_100g": 13.9, "gord_100g": 8.5, "favorito": False},
    {"id": "ali-10", "nome": "Carne patinho moída refogada", "estado": "Cozido", "kcal_100g": 219.0, "carb_100g": 0.0, "prot_100g": 35.9, "gord_100g": 7.3, "favorito": False},
]

MODALIDADES_INICIAIS = [
    {"nome": "Guerreiro Ninja Americano (Ninja Warrior)", "kcal_min": 10.5, "foco": "Pegada, força explosiva, agilidade e obstáculos"},
    {"nome": "Parkour", "kcal_min": 9.5, "foco": "Saltos, precisão, potência de pernas e controle corporal"},
    {"nome": "Skate", "kcal_min": 7.5, "foco": "Equilíbrio, pernas, manobras e sessões de pista/rua"},
    {"nome": "CrossFit", "kcal_min": 10.5, "foco": "WODs de alta intensidade, força e condicionamento"},
    {"nome": "Academia (Musculação)", "kcal_min": 6.5, "foco": "Hipertrofia, força muscular e resistência"},
    {"nome": "Corrida", "kcal_min": 10.0, "foco": "Cardio, resistência aeróbica e ritmo"},
    {"nome": "Natação", "kcal_min": 8.5, "foco": "Corpo inteiro, respiração e baixo impacto articular"},
    {"nome": "Ciclismo / Bike", "kcal_min": 8.0, "foco": "Cardio, pernas e resistência"},
    {"nome": "Caminhada", "kcal_min": 4.8, "foco": "Movimento contínuo, passeio e recuperação ativa"},
    {"nome": "Calistenia", "kcal_min": 7.8, "foco": "Peso corporal, barras, paralelas e core"},
    {"nome": "Treino Funcional", "kcal_min": 8.2, "foco": "Agilidade, estabilidade e coordenação"},
    {"nome": "Lutas / Artes Marciais", "kcal_min": 9.8, "foco": "Explosão, cardio, reflexos e condicionamento"},
    {"nome": "Futebol / Futsal", "kcal_min": 9.2, "foco": "Tiros rápidos, deslocamentos e resistência"},
    {"nome": "Beach Tennis / Vôlei / Basquete", "kcal_min": 8.0, "foco": "Saltos, reação rápida e quadra/areia"},
    {"nome": "Dança", "kcal_min": 6.8, "foco": "Ritmo, coordenação e gasto calórico divertido"},
    {"nome": "Yoga / Mobilidade", "kcal_min": 3.5, "foco": "Flexibilidade, respiração e alongamento"},
]

CONFIG_GLICEMIA_PADRAO = {
    "alvo_min": 70.0,
    "alvo_max": 180.0,
    "alerta_alto": 250.0,
    "carb_por_unidade_insulina": 15.0,
    "fator_correcao_mgdl": 50.0,
    "alvo_correcao": 120.0,
}

METAS_DIARIAS_PADRAO = {
    "meta_kcal_dia": 2200.0,
    "meta_carb_dia": 220.0,
    "meta_treino_kcal_dia": 400.0,
}


def _estado_base_vazio():
    return {
        "perfil_ativo": "Eduardo (Principal)",
        "perfis": ["Eduardo (Principal)"],
        "alimentos": list(ALIMENTOS_INICIAIS),
        "pratos_prontos": [],
        "refeicoes": [],
        "modalidades": list(MODALIDADES_INICIAIS),
        "treinos": [],
        "registros_glicemia": [],
        "config_glicemia": dict(CONFIG_GLICEMIA_PADRAO),
        "metas_diarias": dict(METAS_DIARIAS_PADRAO),
    }


def _normalizar_dados(dados):
    dados.setdefault("perfil_ativo", "Eduardo (Principal)")
    dados.setdefault("perfis", [dados["perfil_ativo"]])
    if dados["perfil_ativo"] not in dados["perfis"]:
        dados["perfis"].append(dados["perfil_ativo"])
    dados.setdefault("alimentos", list(ALIMENTOS_INICIAIS))
    dados.setdefault("pratos_prontos", [])
    dados.setdefault("refeicoes", [])
    dados.setdefault("modalidades", list(MODALIDADES_INICIAIS))
    dados.setdefault("treinos", [])
    dados.setdefault("registros_glicemia", [])

    cfg = dados.setdefault("config_glicemia", dict(CONFIG_GLICEMIA_PADRAO))
    for k, v in CONFIG_GLICEMIA_PADRAO.items():
        cfg.setdefault(k, v)

    metas = dados.setdefault("metas_diarias", dict(METAS_DIARIAS_PADRAO))
    for k, v in METAS_DIARIAS_PADRAO.items():
        metas.setdefault(k, v)

    return dados


def _abrir_conexao():
    db_dir = os.path.dirname(os.path.abspath(DATABASE_PATH))
    if db_dir:
        os.makedirs(db_dir, exist_ok=True)
    conn = sqlite3.connect(DATABASE_PATH)
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS estado_app (
            chave TEXT PRIMARY KEY,
            conteudo TEXT NOT NULL
        )
        """
    )
    conn.commit()
    return conn


def carregar_dados():
    with _abrir_conexao() as conn:
        row = conn.execute("SELECT conteudo FROM estado_app WHERE chave = 'principal'").fetchone()
        if row:
            return _normalizar_dados(json.loads(row[0]))

        if os.path.exists(ARQUIVO_JSON_LEGADO):
            with open(ARQUIVO_JSON_LEGADO, "r", encoding="utf-8") as f:
                dados = _normalizar_dados(json.load(f))
        else:
            dados = _estado_base_vazio()

        conn.execute(
            "INSERT OR REPLACE INTO estado_app (chave, conteudo) VALUES ('principal', ?)",
            (json.dumps(dados, ensure_ascii=False),),
        )
        conn.commit()
        return dados


def salvar_dados(dados):
    normalizado = _normalizar_dados(dados)
    with _abrir_conexao() as conn:
        conn.execute(
            "INSERT OR REPLACE INTO estado_app (chave, conteudo) VALUES ('principal', ?)",
            (json.dumps(normalizado, ensure_ascii=False),),
        )
        conn.commit()


def parse_num(raw, padrao=None):
    if raw is None or str(raw).strip() == "":
        if padrao is not None:
            return float(padrao)
        raise ValueError("Campo numérico obrigatório.")
    txt = str(raw).strip().replace(" ", "").replace(",", ".")
    return float(txt)


def calcular_por_gramas(alimento, gramas):
    fator = gramas / 100.0
    return {
        "gramas": round(gramas, 1),
        "kcal": round(float(alimento["kcal_100g"]) * fator, 1),
        "carboidratos_g": round(float(alimento["carb_100g"]) * fator, 1),
        "proteinas_g": round(float(alimento["prot_100g"]) * fator, 1),
        "gorduras_g": round(float(alimento["gord_100g"]) * fator, 1),
    }


def classificar_glicemia(valor, cfg):
    alvo_min = float(cfg.get("alvo_min", 70))
    alvo_max = float(cfg.get("alvo_max", 180))
    alerta_alto = float(cfg.get("alerta_alto", 250))

    if valor < alvo_min:
        return {
            "status": "baixa",
            "rotulo": "Abaixo da faixa alvo",
            "orientacao": "Apoio educativo: registre o valor e siga o plano combinado com sua equipe de saúde para correção segura e rechecagem.",
        }
    if valor > alerta_alto:
        return {
            "status": "muito_alta",
            "rotulo": "Muito acima da faixa",
            "orientacao": "Apoio educativo: mantenha hidratação com água, evite esforços intensos sem orientação prévia e siga o protocolo da sua equipe médica.",
        }
    if valor > alvo_max:
        return {
            "status": "alta",
            "rotulo": "Acima da faixa alvo",
            "orientacao": "Apoio educativo: observe refeições recentes, treinos e orientações médicas antes de qualquer ajuste de dose.",
        }
    return {
        "status": "alvo",
        "rotulo": "Dentro da faixa alvo",
        "orientacao": "Apoio educativo: destro dentro da sua faixa configurada. Mantenha o acompanhamento regular de refeições e treinos.",
    }


def filtrar_por_perfil(lista, perfil_ativo):
    return [item for item in lista if item.get("perfil", "Eduardo (Principal)") == perfil_ativo]


def resumo_de_data(dados, data_str, perfil_ativo):
    refs = [r for r in filtrar_por_perfil(dados["refeicoes"], perfil_ativo) if r.get("data_hora", "").startswith(data_str)]
    trns = [t for t in filtrar_por_perfil(dados["treinos"], perfil_ativo) if t.get("data_hora", "").startswith(data_str)]
    glcs = [g for g in filtrar_por_perfil(dados["registros_glicemia"], perfil_ativo) if g.get("data_hora", "").startswith(data_str)]

    kcal_comidas = round(sum(float(r.get("kcal", 0)) for r in refs), 1)
    carb = round(sum(float(r.get("carboidratos_g", 0)) for r in refs), 1)
    prot = round(sum(float(r.get("proteinas_g", 0)) for r in refs), 1)
    gord = round(sum(float(r.get("gorduras_g", 0)) for r in refs), 1)
    gramas = round(sum(float(r.get("gramas", 0)) for r in refs), 1)

    kcal_perdidas = round(sum(float(t.get("kcal_perdidas", 0)) for t in trns), 1)
    minutos_treino = round(sum(float(t.get("duracao_min", 0)) for t in trns), 1)
    saldo_kcal = round(kcal_comidas - kcal_perdidas, 1)

    destros = [g["glicemia_mgdl"] for g in glcs if g.get("glicemia_mgdl") is not None]
    ultimo_destro = destros[-1] if destros else None
    media_destro = round(sum(float(x) for x in destros) / len(destros), 1) if destros else None
    insulina_u = round(sum(float(g.get("insulina_u", 0) or 0) for g in glcs), 1)

    return {
        "data": data_str,
        "gramas": gramas,
        "kcal_consumidas": kcal_comidas,
        "kcal_perdidas": kcal_perdidas,
        "saldo_kcal": saldo_kcal,
        "minutos_treino": minutos_treino,
        "carboidratos_g": carb,
        "proteinas_g": prot,
        "gorduras_g": gord,
        "ultimo_destro": ultimo_destro,
        "media_destro": media_destro,
        "insulina_u": insulina_u,
        "qtd_refeicoes": len(refs),
        "qtd_treinos": len(trns),
        "qtd_glicemias": len(glcs),
    }


def montar_estado(dados):
    perfil_ativo = dados.get("perfil_ativo", "Eduardo (Principal)")
    hoje = datetime.now()
    hoje_str = hoje.strftime("%d/%m/%Y")

    refeicoes_hoje = [r for r in filtrar_por_perfil(dados["refeicoes"], perfil_ativo) if r.get("data_hora", "").startswith(hoje_str)]
    treinos_hoje = [t for t in filtrar_por_perfil(dados["treinos"], perfil_ativo) if t.get("data_hora", "").startswith(hoje_str)]
    glicemias_hoje = [g for g in filtrar_por_perfil(dados["registros_glicemia"], perfil_ativo) if g.get("data_hora", "").startswith(hoje_str)]
    pratos_perfil = filtrar_por_perfil(dados["pratos_prontos"], perfil_ativo)

    totais_hoje = resumo_de_data(dados, hoje_str, perfil_ativo)

    por_refeicao = {}
    for item in refeicoes_hoje:
        tipo = item.get("refeicao_tipo", "Refeição")
        grupo = por_refeicao.setdefault(tipo, {"gramas": 0.0, "kcal": 0.0, "carboidratos_g": 0.0, "itens": 0})
        grupo["gramas"] = round(grupo["gramas"] + float(item.get("gramas", 0)), 1)
        grupo["kcal"] = round(grupo["kcal"] + float(item.get("kcal", 0)), 1)
        grupo["carboidratos_g"] = round(grupo["carboidratos_g"] + float(item.get("carboidratos_g", 0)), 1)
        grupo["itens"] += 1

    historico_7_dias = []
    for delta in range(6, -1, -1):
        dia_str = (hoje - timedelta(days=delta)).strftime("%d/%m/%Y")
        historico_7_dias.append(resumo_de_data(dados, dia_str, perfil_ativo))

    linhas_resumo = [
        f"FIRE FIT • Resumo ({perfil_ativo}) — {hoje_str}",
        f"Refeições: {totais_hoje['kcal_consumidas']} kcal | {totais_hoje['carboidratos_g']}g carb | {totais_hoje['proteinas_g']}g prot | {totais_hoje['gramas']}g pesados",
        f"Treinos: -{totais_hoje['kcal_perdidas']} kcal ({totais_hoje['minutos_treino']} min) | Saldo líquido: {totais_hoje['saldo_kcal']} kcal",
    ]
    if totais_hoje["ultimo_destro"] is not None:
        linhas_resumo.append(
            f"Glicemia/Insulina: Último destro {totais_hoje['ultimo_destro']} mg/dL (Média {totais_hoje['media_destro']} mg/dL) | Insulina {totais_hoje['insulina_u']}U"
        )
    else:
        linhas_resumo.append(f"Glicemia/Insulina: Sem destro hoje | Insulina {totais_hoje['insulina_u']}U")
    linhas_resumo.append("Apoio educativo no dia a dia — não substitui profissionais de saúde.")

    return {
        "perfil_ativo": perfil_ativo,
        "perfis": dados["perfis"],
        "alimentos": dados["alimentos"],
        "pratos_prontos": pratos_perfil,
        "refeicoes_hoje": refeicoes_hoje,
        "modalidades": dados["modalidades"],
        "treinos_hoje": treinos_hoje,
        "glicemias_hoje": glicemias_hoje,
        "config_glicemia": dados["config_glicemia"],
        "metas_diarias": dados["metas_diarias"],
        "totais_hoje": totais_hoje,
        "resumo_por_refeicao": por_refeicao,
        "historico_7_dias": historico_7_dias,
        "texto_resumo_dia": "\n".join(linhas_resumo),
        "persistencia": {
            "engine": "SQLite",
            "database_path": DATABASE_PATH,
            "postgres_url_configurada": bool(DATABASE_URL),
        },
        "aviso_apoio": "Apoio educativo ao dia a dia • Não substitui profissionais de saúde",
    }


@app.route("/health")
def health():
    carregar_dados()
    return jsonify({"status": "ok", "engine": "sqlite"}), 200


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/estado")
def api_estado():
    return jsonify(montar_estado(carregar_dados()))


@app.route("/api/perfil", methods=["POST"])
def api_perfil():
    payload = request.get_json(silent=True) or {}
    nome = str(payload.get("perfil", "")).strip()
    if not nome:
        return jsonify({"erro": "Informe o nome do perfil."}), 400

    dados = carregar_dados()
    if nome not in dados["perfis"]:
        dados["perfis"].append(nome)
    dados["perfil_ativo"] = nome
    salvar_dados(dados)
    return jsonify({"ok": True, "estado": montar_estado(dados)})


@app.route("/api/metas", methods=["POST"])
def api_salvar_metas():
    payload = request.get_json(silent=True) or {}
    try:
        meta_kcal = parse_num(payload.get("meta_kcal_dia"), 2200)
        meta_carb = parse_num(payload.get("meta_carb_dia"), 220)
        meta_treino = parse_num(payload.get("meta_treino_kcal_dia"), 400)
        if min(meta_kcal, meta_carb, meta_treino) <= 0:
            raise ValueError()
    except ValueError:
        return jsonify({"erro": "Informe metas diárias maiores que zero."}), 400

    dados = carregar_dados()
    dados["metas_diarias"] = {
        "meta_kcal_dia": round(meta_kcal, 1),
        "meta_carb_dia": round(meta_carb, 1),
        "meta_treino_kcal_dia": round(meta_treino, 1),
    }
    salvar_dados(dados)
    return jsonify({"ok": True, "estado": montar_estado(dados)})


@app.route("/api/alimentos", methods=["POST"])
def api_add_alimento():
    payload = request.get_json(silent=True) or {}
    nome = str(payload.get("nome", "")).strip()
    estado = str(payload.get("estado", "Cozido")).strip() or "Cozido"
    if not nome:
        return jsonify({"erro": "Informe o nome do alimento."}), 400

    try:
        kcal_100g = parse_num(payload.get("kcal_100g"))
        carb_100g = parse_num(payload.get("carb_100g"), 0)
        prot_100g = parse_num(payload.get("prot_100g"), 0)
        gord_100g = parse_num(payload.get("gord_100g"), 0)
        if min(kcal_100g, carb_100g, prot_100g, gord_100g) < 0:
            raise ValueError()
    except ValueError:
        return jsonify({"erro": "Informe valores nutricionais válidos por 100 g."}), 400

    dados = carregar_dados()
    novo = {
        "id": f"ali-{uuid.uuid4().hex[:8]}",
        "nome": nome,
        "estado": estado,
        "kcal_100g": round(kcal_100g, 1),
        "carb_100g": round(carb_100g, 1),
        "prot_100g": round(prot_100g, 1),
        "gord_100g": round(gord_100g, 1),
        "favorito": bool(payload.get("favorito", True)),
    }
    dados["alimentos"].append(novo)
    salvar_dados(dados)
    return jsonify({"ok": True, "alimento": novo, "estado": montar_estado(dados)})


@app.route("/api/refeicoes", methods=["POST"])
def api_add_refeicao():
    payload = request.get_json(silent=True) or {}
    refeicao_tipo = str(payload.get("refeicao_tipo", "Almoço")).strip() or "Almoço"
    alimento_id = str(payload.get("alimento_id", "")).strip()

    try:
        gramas = parse_num(payload.get("gramas"))
        if gramas <= 0:
            raise ValueError()
    except ValueError:
        return jsonify({"erro": "Informe um peso em gramas maior que zero."}), 400

    dados = carregar_dados()
    alimento = next((a for a in dados["alimentos"] if a["id"] == alimento_id), None)
    if not alimento:
        return jsonify({"erro": "Selecione um alimento válido."}), 404

    macros = calcular_por_gramas(alimento, gramas)
    item = {
        "id": f"ref-{uuid.uuid4().hex[:8]}",
        "perfil": dados.get("perfil_ativo", "Eduardo (Principal)"),
        "refeicao_tipo": refeicao_tipo,
        "alimento_id": alimento["id"],
        "alimento": alimento["nome"],
        "estado_preparo": alimento.get("estado", ""),
        **macros,
        "data_hora": datetime.now().strftime("%d/%m/%Y %H:%M"),
    }
    dados["refeicoes"].append(item)
    salvar_dados(dados)
    return jsonify({"ok": True, "item": item, "estado": montar_estado(dados)})


@app.route("/api/refeicoes/<item_id>", methods=["DELETE"])
def api_del_refeicao(item_id):
    dados = carregar_dados()
    antes = len(dados["refeicoes"])
    dados["refeicoes"] = [r for r in dados["refeicoes"] if r.get("id") != item_id]
    if len(dados["refeicoes"]) == antes:
        return jsonify({"erro": "Item não encontrado."}), 404
    salvar_dados(dados)
    return jsonify({"ok": True, "estado": montar_estado(dados)})


@app.route("/api/pratos-prontos", methods=["POST"])
def api_salvar_prato_pronto():
    payload = request.get_json(silent=True) or {}
    nome_prato = str(payload.get("nome", "")).strip()
    refeicao_origem = str(payload.get("refeicao_tipo", "")).strip()
    if not nome_prato:
        return jsonify({"erro": "Dê um nome ao prato pronto (ex.: Almoço Padrão)."}), 400

    dados = carregar_dados()
    perfil_ativo = dados.get("perfil_ativo", "Eduardo (Principal)")
    hoje_str = datetime.now().strftime("%d/%m/%Y")
    itens = [
        {
            "alimento_id": r["alimento_id"],
            "alimento": r["alimento"],
            "gramas": r["gramas"],
        }
        for r in filtrar_por_perfil(dados["refeicoes"], perfil_ativo)
        if r.get("data_hora", "").startswith(hoje_str)
        and (not refeicao_origem or r.get("refeicao_tipo") == refeicao_origem)
    ]
    if not itens:
        return jsonify({"erro": "Adicione alimentos na refeição antes de salvar como prato pronto."}), 400

    prato = {
        "id": f"prt-{uuid.uuid4().hex[:8]}",
        "perfil": perfil_ativo,
        "nome": nome_prato,
        "itens": itens,
    }
    dados["pratos_prontos"].append(prato)
    salvar_dados(dados)
    return jsonify({"ok": True, "estado": montar_estado(dados)})


@app.route("/api/pratos-prontos/<prato_id>/lancar", methods=["POST"])
def api_lancar_prato_pronto(prato_id):
    payload = request.get_json(silent=True) or {}
    refeicao_tipo = str(payload.get("refeicao_tipo", "Almoço")).strip() or "Almoço"

    dados = carregar_dados()
    perfil_ativo = dados.get("perfil_ativo", "Eduardo (Principal)")
    prato = next((p for p in dados["pratos_prontos"] if p["id"] == prato_id), None)
    if not prato:
        return jsonify({"erro": "Prato pronto não encontrado."}), 404

    agora = datetime.now().strftime("%d/%m/%Y %H:%M")
    for it in prato["itens"]:
        alimento = next((a for a in dados["alimentos"] if a["id"] == it["alimento_id"]), None)
        if not alimento:
            continue
        macros = calcular_por_gramas(alimento, float(it["gramas"]))
        dados["refeicoes"].append({
            "id": f"ref-{uuid.uuid4().hex[:8]}",
            "perfil": perfil_ativo,
            "refeicao_tipo": refeicao_tipo,
            "alimento_id": alimento["id"],
            "alimento": alimento["nome"],
            "estado_preparo": alimento.get("estado", ""),
            **macros,
            "data_hora": agora,
        })

    salvar_dados(dados)
    return jsonify({"ok": True, "estado": montar_estado(dados)})


@app.route("/api/modalidades", methods=["POST"])
def api_add_modalidade():
    payload = request.get_json(silent=True) or {}
    nome = str(payload.get("nome", "")).strip()
    foco = str(payload.get("foco", "Treino personalizado")).strip() or "Treino personalizado"
    if not nome:
        return jsonify({"erro": "Informe o nome da modalidade."}), 400

    try:
        kcal_min = parse_num(payload.get("kcal_min"), 7.0)
        if kcal_min <= 0:
            raise ValueError()
    except ValueError:
        return jsonify({"erro": "Informe uma estimativa de kcal/min maior que zero."}), 400

    dados = carregar_dados()
    if not any(m["nome"].lower() == nome.lower() for m in dados["modalidades"]):
        dados["modalidades"].append({
            "nome": nome,
            "kcal_min": round(kcal_min, 1),
            "foco": foco,
        })
        salvar_dados(dados)

    return jsonify({"ok": True, "estado": montar_estado(dados)})


@app.route("/api/treinos", methods=["POST"])
def api_add_treino():
    payload = request.get_json(silent=True) or {}
    modalidade = str(payload.get("modalidade", "")).strip()
    titulo = str(payload.get("titulo", "")).strip()
    intensidade = str(payload.get("intensidade", "Moderada")).strip() or "Moderada"
    observacao = str(payload.get("observacao", "")).strip()

    if not modalidade:
        return jsonify({"erro": "Selecione ou digite uma modalidade."}), 400

    try:
        duracao_min = parse_num(payload.get("duracao_min"))
        kcal_perdidas = parse_num(payload.get("kcal_perdidas"))
        if duracao_min <= 0 or kcal_perdidas < 0:
            raise ValueError()
    except ValueError:
        return jsonify({"erro": "Informe duração em minutos e calorias perdidas válidas."}), 400

    dados = carregar_dados()
    if not any(m["nome"].lower() == modalidade.lower() for m in dados["modalidades"]):
        estimativa = round(kcal_perdidas / duracao_min, 1) if duracao_min > 0 else 7.0
        dados["modalidades"].append({
            "nome": modalidade,
            "kcal_min": max(1.0, estimativa),
            "foco": titulo or "Modalidade adicionada no treino",
        })

    treino = {
        "id": f"trn-{uuid.uuid4().hex[:8]}",
        "perfil": dados.get("perfil_ativo", "Eduardo (Principal)"),
        "modalidade": modalidade,
        "titulo": titulo or f"Treino de {modalidade}",
        "intensidade": intensidade,
        "duracao_min": round(duracao_min, 1),
        "kcal_perdidas": round(kcal_perdidas, 1),
        "observacao": observacao,
        "data_hora": datetime.now().strftime("%d/%m/%Y %H:%M"),
    }
    dados["treinos"].append(treino)
    salvar_dados(dados)
    return jsonify({"ok": True, "treino": treino, "estado": montar_estado(dados)})


@app.route("/api/treinos/<treino_id>", methods=["DELETE"])
def api_del_treino(treino_id):
    dados = carregar_dados()
    antes = len(dados["treinos"])
    dados["treinos"] = [t for t in dados["treinos"] if t.get("id") != treino_id]
    if len(dados["treinos"]) == antes:
        return jsonify({"erro": "Treino não encontrado."}), 404
    salvar_dados(dados)
    return jsonify({"ok": True, "estado": montar_estado(dados)})


@app.route("/api/glicemia", methods=["POST"])
def api_add_glicemia():
    payload = request.get_json(silent=True) or {}
    momento = str(payload.get("momento", "Pré-refeição")).strip() or "Pré-refeição"
    tipo_insulina = str(payload.get("tipo_insulina", "Rápida / Bolus")).strip() or "Rápida / Bolus"
    observacao = str(payload.get("observacao", "")).strip()

    raw_glic = payload.get("glicemia_mgdl")
    raw_ins = payload.get("insulina_u")

    try:
        glicemia = parse_num(raw_glic) if (raw_glic is not None and str(raw_glic).strip() != "") else None
        insulina = parse_num(raw_ins, 0) if (raw_ins is not None and str(raw_ins).strip() != "") else 0.0
        if glicemia is not None and (glicemia <= 0 or glicemia > 900):
            raise ValueError()
        if insulina < 0:
            raise ValueError()
        if glicemia is None and insulina <= 0:
            return jsonify({"erro": "Informe o destro (mg/dL) ou as unidades de insulina."}), 400
    except ValueError:
        return jsonify({"erro": "Informe valores válidos de destro (mg/dL) e insulina."}), 400

    dados = carregar_dados()
    classif = classificar_glicemia(glicemia, dados["config_glicemia"]) if glicemia is not None else {
        "status": "alvo",
        "rotulo": "Registro de insulina",
        "orientacao": "Apoio educativo: registro de aplicação salvo para acompanhamento do dia.",
    }

    registro = {
        "id": f"glc-{uuid.uuid4().hex[:8]}",
        "perfil": dados.get("perfil_ativo", "Eduardo (Principal)"),
        "momento": momento,
        "glicemia_mgdl": round(glicemia, 1) if glicemia is not None else None,
        "insulina_u": round(insulina, 1),
        "tipo_insulina": tipo_insulina if insulina > 0 else "",
        "status": classif["status"],
        "rotulo_faixa": classif["rotulo"],
        "orientacao": classif["orientacao"],
        "observacao": observacao,
        "data_hora": datetime.now().strftime("%d/%m/%Y %H:%M"),
    }
    dados["registros_glicemia"].append(registro)
    salvar_dados(dados)
    return jsonify({"ok": True, "registro": registro, "estado": montar_estado(dados)})


@app.route("/api/glicemia/<reg_id>", methods=["DELETE"])
def api_del_glicemia(reg_id):
    dados = carregar_dados()
    antes = len(dados["registros_glicemia"])
    dados["registros_glicemia"] = [g for g in dados["registros_glicemia"] if g.get("id") != reg_id]
    if len(dados["registros_glicemia"]) == antes:
        return jsonify({"erro": "Registro não encontrado."}), 404
    salvar_dados(dados)
    return jsonify({"ok": True, "estado": montar_estado(dados)})


@app.route("/api/glicemia/config", methods=["POST"])
def api_salvar_config_glicemia():
    payload = request.get_json(silent=True) or {}
    try:
        alvo_min = parse_num(payload.get("alvo_min"), 70)
        alvo_max = parse_num(payload.get("alvo_max"), 180)
        alerta_alto = parse_num(payload.get("alerta_alto"), 250)
        carb_por_u = parse_num(payload.get("carb_por_unidade_insulina"), 15)
        fator_corr = parse_num(payload.get("fator_correcao_mgdl"), 50)
        alvo_corr = parse_num(payload.get("alvo_correcao"), 120)
        if alvo_min <= 0 or alvo_max <= alvo_min or carb_por_u <= 0 or fator_corr <= 0:
            raise ValueError()
    except ValueError:
        return jsonify({"erro": "Verifique os valores da faixa alvo e dos parâmetros de referência."}), 400

    dados = carregar_dados()
    dados["config_glicemia"] = {
        "alvo_min": round(alvo_min, 1),
        "alvo_max": round(alvo_max, 1),
        "alerta_alto": round(alerta_alto, 1),
        "carb_por_unidade_insulina": round(carb_por_u, 1),
        "fator_correcao_mgdl": round(fator_corr, 1),
        "alvo_correcao": round(alvo_corr, 1),
    }
    salvar_dados(dados)
    return jsonify({"ok": True, "estado": montar_estado(dados)})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5001))
    app.run(debug=True, host="0.0.0.0", port=port)
