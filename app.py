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
    # Cereais, massas, tubérculos e grãos
    "arroz branco": 128,
    "arroz": 128,
    "arroz integral": 124,
    "arroz temperado": 145,
    "feijao": 76,
    "feijão": 76,
    "feijao carioca": 76,
    "feijão carioca": 76,
    "feijao preto": 77,
    "feijão preto": 77,
    "feijao tropeiro": 195,
    "feijão tropeiro": 195,
    "lentilha": 93,
    "grao de bico": 164,
    "grão de bico": 164,
    "ervilha": 81,
    "batata doce": 77,
    "batata-doce": 77,
    "batata inglesa": 52,
    "batata": 52,
    "pure de batata": 113,
    "purê de batata": 113,
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

    # Carnes, aves, peixes e ovos
    "peito de frango": 159,
    "frango": 159,
    "frango grelhado": 159,
    "frango assado": 190,
    "frango desfiado": 165,
    "coxa de frango": 215,
    "sobrecoxa": 232,
    "bife": 219,
    "bife acebolado": 235,
    "patinho": 219,
    "alcatra": 241,
    "picanha": 289,
    "costela": 310,
    "contrafile": 266,
    "contrafilé": 266,
    "acem": 215,
    "acém": 215,
    "carne moida": 212,
    "carne moída": 212,
    "carne magra": 180,
    "carne seca": 313,
    "lombo suino": 197,
    "lombo suíno": 197,
    "tilapia": 96,
    "tilápia": 96,
    "atum": 116,
    "sardinha": 185,
    "salmao": 211,
    "salmão": 211,
    "merluza": 89,
    "bacalhau": 105,
    "camarao": 90,
    "camarão": 90,
    "ovo": 146,
    "ovos": 146,
    "omelete": 154,
    "clara de ovo": 52,

    # Pratos brasileiros e do mundo
    "feijoada": 117,
    "farofa": 406,
    "torresmo": 544,
    "estrogonofe de frango": 168,
    "estrogonofe de carne": 195,
    "estrogonofe": 180,
    "lasanha": 165,
    "macarrao a bolonhesa": 142,
    "macarrão à bolonhesa": 142,
    "macarrao ao molho branco": 168,
    "macarrão ao molho branco": 168,
    "carbonara": 215,
    "risoto": 155,
    "nhoque": 148,
    "panqueca": 185,
    "escondidinho": 170,
    "moqueca": 135,
    "bobó de camarao": 175,
    "bobó de camarão": 175,
    "vatapa": 210,
    "galinhada": 152,
    "sushi": 143,
    "sashimi": 127,
    "temaki": 165,
    "yakisoba": 138,
    "ramen": 120,
    "taco": 226,
    "burrito": 206,
    "quesadilla": 255,
    "guacamole": 160,
    "hummus": 166,
    "falafel": 333,
    "tabule": 95,
    "esfiha": 245,
    "kibe": 195,

    # Laticínios
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
    "queijo parmesao": 431,
    "queijo parmesão": 431,
    "requeijao": 257,
    "requeijão": 257,
    "requeijao light": 181,
    "requeijão light": 181,

    # Frutas
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

    # Legumes, verduras e castanhas
    "brocolis": 25,
    "brócolis": 25,
    "couve": 27,
    "couve refogada": 65,
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
    "salada": 25,
    "castanha de caju": 570,
    "castanha do para": 643,
    "castanha do pará": 643,
    "amendoim": 544,
    "amendoa": 581,
    "amêndoa": 581,
    "chia": 486,
    "linhaca": 495,
    "linhaça": 495,

    # Lanches, embutidos e itens livres
    "peito de peru": 108,
    "presunto": 165,
    "bacon": 541,
    "linguica": 296,
    "linguiça": 296,
    "salsicha": 246,
    "cachorro quente": 248,
    "hot dog": 248,
    "pizza": 266,
    "hamburguer": 295,
    "hambúrguer": 295,
    "nugget": 296,
    "nuggets": 296,
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
    "arroz integral", "frango", "peito de frango", "frango grelhado", "frango desfiado",
    "coxa de frango", "sobrecoxa", "bife", "patinho", "alcatra", "contrafile",
    "contrafilé", "acem", "acém", "carne moida", "carne moída", "carne magra",
    "lombo suino", "lombo suíno", "ovo", "ovos", "omelete", "clara de ovo",
    "banana", "fruta", "frutas", "salada", "legume", "legumes", "brocolis",
    "brócolis", "couve", "alface", "tomate", "pepino", "cenoura", "abobrinha",
    "berinjela", "chuchu", "vagem", "espinafre", "palmito", "aveia", "peixe",
    "tilapia", "tilápia", "atum", "sardinha", "merluza", "bacalhau", "camarao",
    "camarão", "batata doce", "batata-doce", "feijao", "feijão", "lentilha",
    "grao de bico", "grão de bico", "ervilha", "iogurte natural", "iogurte grego",
    "queijo minas", "queijo cottage", "leite desnatado", "leite semidesnatado",
    "castanha", "amendoim", "amendoa", "amêndoa", "chia", "linhaca", "linhaça",
    "abacate", "morango", "maca", "maçã", "mamao", "mamão", "melancia",
    "melao", "melão", "abacaxi", "laranja", "uva", "manga", "pera", "pêra",
    "goiaba", "kiwi", "whey", "salmao", "salmão", "cuscuz", "mandioca",
    "aipim", "macaxeira", "inhame", "cara", "cará", "peito de peru", "tapioca",
    "sushi", "sashimi", "temaki", "hummus", "tabule"
]

PALAVRAS_NAO_SAUDAVEIS = [
    "feijoada", "farofa", "torresmo", "feijao tropeiro", "feijão tropeiro",
    "picanha", "costela", "carne seca", "carbonara", "estrogonofe", "lasanha",
    "fritura", "frito", "frita", "batata frita", "doce", "chocolate", "sorvete",
    "refrigerante", "refri", "pizza", "hamburguer", "hambúrguer", "burger",
    "cachorro quente", "hot dog", "nugget", "nuggets", "salgado", "coxinha",
    "pastel", "empada", "biscoito", "bolacha", "bolo", "pudim", "cerveja",
    "alcool", "álcool", "fast food", "bacon", "linguica", "linguiça", "salsicha",
    "presunto", "maionese", "chantilly", "leite condensado", "quesadilla",
    "falafel", "esfiha", "pao de queijo", "pão de queijo"
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

    if kcal_100g is not None and g > 0:
        auto_val = int(round((g / 100.0) * kcal_100g))
        if kcal_manual not in (None, ""):
            try:
                manual_val = max(0, int(round(float(kcal_manual))))
                return manual_val if manual_val != auto_val else auto_val
            except Exception:
                pass
        return auto_val

    if kcal_manual not in (None, ""):
        try:
            return max(0, int(round(float(kcal_manual))))
        except Exception:
            pass

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
            kcal_item = calcular_kcal_por_gramas(alimento_nome, p.get("gramas"), p.get("kcal"))
            data.setdefault("alimentos", []).insert(0, {
                "data": agora_br(),
                "nome": rotulo,
                "gramas": p.get("gramas"),
                "kcal": kcal_item,
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
