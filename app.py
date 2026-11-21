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

DEFAULT_REFEICOES = [
    {"nome": "Café da manhã", "horario": "08:00"},
    {"nome": "Almoço", "horario": "12:30"},
    {"nome": "Lanche da tarde", "horario": "16:00"},
    {"nome": "Jantar", "horario": "19:30"}
]

DEFAULT_DATA = {
    "perfil": {
        "nome": "",
        "idade": None,
        "altura_cm": None,
        "objetivo": "perda"
    },
    "meta_peso": 75.0,
    "peso_atual": None,
    "agua": {
        "meta_ml": 2500,
        "consumido_ml": 0,
        "data_ref": "",
        "historico": []
    },
    "refeicoes": DEFAULT_REFEICOES,
    "balanca": [],
    "treinos": [],
    "glicemia": [],
    "prato": [],
    "alimentos": [
        {"nome": "Arroz integral (100g)", "kcal": 124, "saudavel": True},
        {"nome": "Peito de frango grelhado (100g)", "kcal": 159, "saudavel": True},
        {"nome": "Ovo cozido (1 un)", "kcal": 78, "saudavel": True},
        {"nome": "Banana prata (1 un)", "kcal": 87, "saudavel": True}
    ]
}

PALAVRAS_SAUDAVEIS = [
    "arroz integral", "frango", "peito de frango", "ovo", "ovos", "banana", "fruta",
    "frutas", "salada", "legume", "legumes", "brocolis", "brócolis", "aveia",
    "peixe", "tilapia", "tilápia", "atum", "batata doce", "feijao", "feijão",
    "iogurte natural", "castanha", "abacate", "morango", "maca", "maçã", "whey",
    "salmao", "salmão", "carne magra", "patinho", "alface", "tomate", "pepino"
]

PALAVRAS_NAO_SAUDAVEIS = [
    "fritura", "frito", "frita", "doce", "chocolate", "sorvete", "refrigerante",
    "refri", "pizza", "hamburguer", "hambúrguer", "burger", "salgado", "coxinha",
    "pastel", "empada", "biscoito", "bolacha", "bolo", "pudim", "cerveja",
    "alcool", "álcool", "fast food", "bacon", "maionese", "chantilly", "leite condensado"
]


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

    hoje = hoje_br()
    if data["agua"].get("data_ref") and data["agua"].get("data_ref") != hoje:
        data["agua"]["consumido_ml"] = 0
        data["agua"]["historico"] = []
    data["agua"]["data_ref"] = hoje

    for item in data.get("prato", []):
        if "saudavel" not in item:
            item["saudavel"] = classificar_saude(item.get("item", ""))

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


def orientacao_instrutor(perfil, peso, meta):
    objetivo = (perfil or {}).get("objetivo", "perda")
    diff = round(peso - meta, 1) if (peso is not None and meta is not None) else None

    if objetivo == "ganho":
        foco = "Ganho de massa"
        base = (
            "Base para o instrutor: priorizar superávit calórico moderado com boa oferta proteica, "
            "treino de força progressivo e constância no sono/recuperação, ajustando conforme resposta."
        )
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
        base = (
            "Base para o instrutor: priorizar déficit calórico sustentável, regularidade de treinos "
            "(força + movimento diário) e atenção às refeições e sinais do dia a dia."
        )
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

    prato_hoje = [x for x in data.get("prato", []) if str(x.get("data", "")).startswith(prefixo_hoje)]
    treinos_hoje = [x for x in data.get("treinos", []) if str(x.get("data", "")).startswith(prefixo_hoje)]
    balanca_hoje = [x for x in data.get("balanca", []) if str(x.get("data", "")).startswith(prefixo_hoje)]
    glicemia_hoje = [x for x in data.get("glicemia", []) if str(x.get("data", "")).startswith(prefixo_hoje)]
    agua = data.get("agua", DEFAULT_DATA["agua"])

    kcal_total = sum(int(x.get("kcal", 0) or 0) for x in prato_hoje)
    qtd_saudaveis = sum(1 for x in prato_hoje if x.get("saudavel", True))
    qtd_nao_saudaveis = sum(1 for x in prato_hoje if not x.get("saudavel", True))

    if not prato_hoje:
        avaliacao_alimentacao = "Sem refeições registradas hoje."
    elif qtd_nao_saudaveis == 0:
        avaliacao_alimentacao = "Alimentação do dia dentro do saudável."
    elif qtd_saudaveis >= qtd_nao_saudaveis:
        avaliacao_alimentacao = f"Predomínio saudável ({qtd_saudaveis} saudáveis vs. {qtd_nao_saudaveis} fora do padrão)."
    else:
        avaliacao_alimentacao = f"Atenção: mais itens fora do saudável hoje ({qtd_nao_saudaveis} vs. {qtd_saudaveis} saudáveis)."

    minutos_treino_hoje = sum(int(x.get("minutos", 0) or 0) for x in treinos_hoje)
    destros_hoje = len(balanca_hoje)
    ultimo_peso_hoje = balanca_hoje[0]["peso"] if balanca_hoje else data.get("peso_atual")

    return {
        "data_hoje": hoje_br_dt().strftime("%d/%m/%Y"),
        "agua_ml": int(agua.get("consumido_ml", 0) or 0),
        "meta_agua_ml": int(agua.get("meta_ml", 2500) or 2500),
        "agua_historico": agua.get("historico", []),
        "kcal_hoje": kcal_total,
        "qtd_saudaveis": qtd_saudaveis,
        "qtd_nao_saudaveis": qtd_nao_saudaveis,
        "avaliacao_alimentacao": avaliacao_alimentacao,
        "prato_hoje": prato_hoje,
        "minutos_treino_hoje": minutos_treino_hoje,
        "treinos_hoje": treinos_hoje,
        "destros_hoje": destros_hoje,
        "ultimo_peso_hoje": ultimo_peso_hoje,
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
    diferenca = round(peso - meta, 1) if (peso is not None and meta is not None) else None
    return jsonify({
        "hora_servidor_br": agora_br_dt().strftime("%H:%M"),
        "perfil": perfil,
        "peso_atual": peso,
        "meta_peso": meta,
        "diferenca_meta": diferenca,
        "orientacao": orientacao_instrutor(perfil, peso, meta),
        "agua": data.get("agua", DEFAULT_DATA["agua"]),
        "refeicoes": data.get("refeicoes", DEFAULT_REFEICOES),
        "balanca": data.get("balanca", []),
        "treinos": data.get("treinos", []),
        "glicemia": data.get("glicemia", []),
        "prato": data.get("prato", []),
        "alimentos": data.get("alimentos", []),
        "resumo_dia": montar_resumo_dia(data)
    })


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


@app.route("/api/prato", methods=["POST"])
def add_prato():
    payload = request.get_json(force=True) or {}
    data = load_data()
    item_nome = str(payload.get("item", "")).strip()
    saudavel_flag = classificar_saude(item_nome, payload.get("saude_tipo"))
    data["prato"].insert(0, {
        "data": agora_br(),
        "item": item_nome,
        "kcal": int(payload.get("kcal", 0) or 0),
        "saudavel": saudavel_flag
    })
    save_data(data)
    return jsonify({"ok": True})


@app.route("/api/alimentos", methods=["POST"])
def add_alimento():
    payload = request.get_json(force=True) or {}
    data = load_data()
    nome_alimento = str(payload.get("nome", "")).strip()
    data["alimentos"].insert(0, {
        "nome": nome_alimento,
        "kcal": int(payload.get("kcal", 0) or 0),
        "saudavel": classificar_saude(nome_alimento, payload.get("saude_tipo"))
    })
    save_data(data)
    return jsonify({"ok": True})


@app.route("/api/excluir/<categoria>/<int:idx>", methods=["DELETE"])
def excluir_item(categoria, idx):
    permitidos = {"balanca", "treinos", "glicemia", "prato", "alimentos"}
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
