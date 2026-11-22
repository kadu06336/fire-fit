from datetime import datetime
import json
import os
import re
from zoneinfo import ZoneInfo
from flask import Flask, jsonify, render_template, request

try:
import psycopg2
except ImportError:
psycopg2 = None

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DADOS_JSON = os.path.join(BASE_DIR, "dados_fire_fit.json")
TZ_BR = ZoneInfo("America/Sao_Paulo")
DIAS_SEMANA = ["Segunda", "Terça", "Quarta", "Quinta", "Sexta", "Sábado", "Domingo"]

DEFAULT_REFEICOES = [
{"nome": "Café da manhã", "horario": "08:00"},
{"nome": "Almoço", "horario": "12:30"},
{"nome": "Lanche da tarde", "horario": "16:00"},
{"nome": "Jantar", "horario": "19:30"},
]

TABELA_KCAL_100G = {
"arroz branco": 128, "arroz": 128, "arroz integral": 124,
"feijão": 76, "feijao": 76, "peito de frango": 159,
"frango grelhado": 159, "frango": 159, "bife": 163,
"carne bovina": 219, "ovo cozido": 146, "ovo": 146,
"batata-doce": 77, "batata doce": 77, "batata inglesa": 52,
"macarrão": 124, "macarrao": 124, "pão francês": 300,
"pao frances": 300, "pão integral": 253, "pao integral": 253,
"banana": 98, "aveia": 394, "queijo muçarela": 300,
"queijo mucarela": 300, "azeite": 884,
}

PALAVRAS_NAO_SAUDAVEIS = [
"fritura", "frito", "refrigerante", "doce", "bolo", "biscoito",
"salgadinho", "torresmo", "pizza", "hambúrguer", "hamburguer", "açúcar", "acucar",
]


def criar_estado_vazio(nome_usuario="Padrao"):
return {
    "perfil": {"nome": nome_usuario, "idade": None, "altura_cm": None, "objetivo": "perda"},
    "meta_peso": 75.0,
    "peso_atual": None,
    "meta_kcal_dia": 1500,
    "agua": {"meta_ml": 2500, "consumido_ml": 0, "data_ref": "", "historico": []},
    "refeicoes": json.loads(json.dumps(DEFAULT_REFEICOES)),
    "cardapio_semana": [],
    "balanca": [],
    "treinos": [],
    "glicemia": [],
    "alimentos": [],
}


DEFAULT_STORE = {
"usuario_ativo": "eduardo",
"usuarios": {
    "eduardo": criar_estado_vazio("Eduardo")
}
}

app = Flask(__name__, template_folder=os.path.join(BASE_DIR, "templates"), static_folder=BASE_DIR)
app.secret_key = os.environ.get("SECRET_KEY", "fire-fit-secret-key")


def sanitizar_chave_usuario(chave):
limpo = re.sub(r"[^a-zA-Z0-9_-]+", "_", (chave or "").strip().lower()).strip("_")
return limpo[:32] if limpo else "eduardo"


def agora_br_dt():
return datetime.now(TZ_BR)


def hoje_br():
return agora_br_dt().strftime("%Y-%m-%d")


def hoje_br_curto():
return agora_br_dt().strftime("%d/%m")


def agora_br():
return agora_br_dt().strftime("%d/%m %H:%M")


def _to_float(val, padrao=None):
if val is None or val == "":
    return padrao
try:
    return float(str(val).replace(",", ".").strip())
except Exception:
    return padrao


def _to_int(val, padrao=0):
num = _to_float(val, None)
return int(round(num)) if num is not None else padrao


def classificar_saude(nome_alimento, tipo_saude=None):
if tipo_saude in ("saudavel", "nao_saudavel"):
    return tipo_saude == "saudavel"
texto = (nome_alimento or "").lower()
return not any(p in texto for p in PALAVRAS_NAO_SAUDAVEIS)


def buscar_kcal_por_100g(nome_alimento):
texto = (nome_alimento or "").lower()
for chave in sorted(TABELA_KCAL_100G.keys(), key=len, reverse=True):
    if chave in texto:
        return TABELA_KCAL_100G[chave]
return None


def calcular_kcal_por_gramas(nome_alimento, gramas, kcal_100g_manual=None, kcal_item_manual=None):
g = _to_float(gramas, 0.0) or 0.0
kcal_100 = _to_float(kcal_100g_manual, None)
if kcal_100 is None or kcal_100 <= 0:
    kcal_100 = buscar_kcal_por_100g(nome_alimento)
if kcal_100 is not None and kcal_100 > 0 and g > 0:
    return int(round((g / 100.0) * float(kcal_100)))
kcal_item = _to_float(kcal_item_manual, None)
if kcal_item is not None and kcal_item >= 0:
    return int(round(kcal_item))
return int(round(kcal_100)) if (kcal_100 is not None and kcal_100 > 0) else 0


def avaliar_calorias_dia(kcal_consumidas, meta_kcal, objetivo="perda", qtd_nao_saudaveis=0):
consumido = _to_int(kcal_consumidas, 0)
meta = max(1, _to_int(meta_kcal, 1500))
diff = consumido - meta
foco_txt = "ganho de massa" if objetivo == "ganho" else "perda de peso"
saude_txt = "Atenção: há item não saudável hoje" if qtd_nao_saudaveis > 0 else "Saudável"
st_saude = "nao_saudavel" if qtd_nao_saudaveis > 0 else "saudavel"
if diff > 0:
    return {
        "status": "passou", "faltam": 0, "passou": diff,
        "saude_status": st_saude, "saude_texto": saude_txt,
        "mensagem": f"Já consumiu {consumido} kcal e passou {diff} kcal da meta de {meta} kcal ({foco_txt}).",
    }
if diff < 0:
    return {
        "status": "faltando", "faltam": abs(diff), "passou": 0,
        "saude_status": st_saude, "saude_texto": saude_txt,
        "mensagem": f"Já consumiu {consumido} kcal de {meta} kcal — faltam {abs(diff)} kcal ({foco_txt}).",
    }
return {
    "status": "na_meta", "faltam": 0, "passou": 0,
    "saude_status": st_saude, "saude_texto": saude_txt,
    "mensagem": f"Já consumiu {consumido} kcal e atingiu a meta de {meta} kcal ({foco_txt}).",
}


def orientacao_instrutor(perfil, peso, meta, meta_kcal):
objetivo = (perfil or {}).get("objetivo", "perda")
diff = round(peso - meta, 1) if (peso is not None and meta is not None) else None
if objetivo == "ganho":
    foco, base = "Ganho de massa", f"Meta diária definida pelo instrutor: {meta_kcal} kcal/dia para ganho de massa."
    meta_txt = (
        "Informe peso atual e meta para acompanhar."
        if diff is None
        else (
            f"Faltam {abs(diff)} kg para atingir a meta de ganho."
            if diff < 0
            else (f"Acima da meta de ganho em {diff} kg." if diff > 0 else "Meta de peso atingida!")
        )
    )
else:
    foco, base = "Perda de peso", f"Meta diária definida pelo instrutor: {meta_kcal} kcal/dia para perda de peso."
    meta_txt = (
        "Informe peso atual e meta para acompanhar."
        if diff is None
        else (
            f"Restam {diff} kg para chegar à meta de peso."
            if diff > 0
            else (f"Abaixo da meta em {abs(diff)} kg." if diff < 0 else "Meta de peso atingida!")
        )
    )
return {"foco": foco, "texto": f"{base} {meta_txt}"}


def normalizar_usuario_data(raw, chave="eduardo"):
base = criar_estado_vazio(chave.capitalize())
data = json.loads(json.dumps(base))
if isinstance(raw, dict):
    for k, v in raw.items():
        data[k] = v
if not isinstance(data.get("perfil"), dict):
    data["perfil"] = json.loads(json.dumps(base["perfil"]))
if not data["perfil"].get("nome"):
    data["perfil"]["nome"] = chave.capitalize()
if not isinstance(data.get("agua"), dict):
    data["agua"] = json.loads(json.dumps(base["agua"]))
else:
    for ak, av in base["agua"].items():
        if ak not in data["agua"]:
            data["agua"][ak] = json.loads(json.dumps(av))
if not isinstance(data.get("refeicoes"), list) or not data["refeicoes"]:
    data["refeicoes"] = json.loads(json.dumps(DEFAULT_REFEICOES))
if not isinstance(data.get("cardapio_semana"), list):
    data["cardapio_semana"] = []
for cat in ("balanca", "treinos", "glicemia", "alimentos"):
    if not isinstance(data.get(cat), list):
        data[cat] = []
data["meta_kcal_dia"] = max(200, _to_int(data.get("meta_kcal_dia"), 1500))
hoje = hoje_br()
if data["agua"].get("data_ref") and data["agua"].get("data_ref") != hoje:
    data["agua"]["consumido_ml"] = 0
    data["agua"]["historico"] = []
data["agua"]["data_ref"] = hoje
for item in data["alimentos"]:
    if "saudavel" not in item:
        item["saudavel"] = classificar_saude(item.get("nome", ""))
    if not item.get("data"):
        item["data"] = agora_br()
    g = _to_float(item.get("gramas"), None)
    item["gramas"] = g
    k100 = _to_float(item.get("kcal_100g"), None)
    item["kcal"] = (
        calcular_kcal_por_gramas(item.get("nome", ""), g, k100, None)
        if (k100 is not None and g and g > 0)
        else _to_int(item.get("kcal"), 0)
    )
for prato in data["cardapio_semana"]:
    if prato.get("dia", "Segunda") not in DIAS_SEMANA:
        prato["dia"] = "Segunda"
    if not prato.get("refeicao"):
        prato["refeicao"] = "Almoço"
    porcoes = prato.get("porcoes") if isinstance(prato.get("porcoes"), list) else []
    norm = []
    for p in porcoes:
        nome_p = str(p.get("alimento") or p.get("nome") or "").strip()
        if not nome_p:
            continue
        g_p = _to_float(p.get("gramas") if p.get("gramas") is not None else p.get("quantidade"), None)
        k100_p = _to_float(p.get("kcal_100g"), None)
        kcal_p = calcular_kcal_por_gramas(nome_p, g_p, k100_p, p.get("kcal"))
        norm.append({
            "alimento": nome_p, "gramas": g_p, "kcal_100g": k100_p,
            "kcal": kcal_p, "saudavel": bool(p.get("saudavel", classificar_saude(nome_p))),
        })
    prato["porcoes"] = norm
    prato["total_kcal"] = sum(_to_int(x.get("kcal"), 0) for x in norm)
return data


def normalizar_store(raw):
store = {"usuario_ativo": "eduardo", "usuarios": {}}
if isinstance(raw, dict):
    if isinstance(raw.get("usuarios"), dict) and raw["usuarios"]:
        store["usuario_ativo"] = sanitizar_chave_usuario(raw.get("usuario_ativo") or "eduardo")
        for k, v in raw["usuarios"].items():
            sk = sanitizar_chave_usuario(k)
            store["usuarios"][sk] = normalizar_usuario_data(v, sk)
    elif any(k in raw for k in ("perfil", "alimentos", "agua", "treinos", "balanca", "glicemia", "cardapio_semana")):
        store["usuarios"]["eduardo"] = normalizar_usuario_data(raw, "eduardo")
if "eduardo" not in store["usuarios"]:
    store["usuarios"]["eduardo"] = normalizar_usuario_data({}, "eduardo")
if store["usuario_ativo"] not in store["usuarios"]:
    store["usuario_ativo"] = next(iter(store["usuarios"].keys()))
return store


def _db_url():
return (os.environ.get("DATABASE_URL") or "").strip()


def _garantir_tabela_pg(conn):
with conn.cursor() as cur:
    cur.execute(
        "CREATE TABLE IF NOT EXISTS fire_fit_estado ("
        "id INTEGER PRIMARY KEY, payload JSONB NOT NULL, atualizado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP)"
    )
    cur.execute("SELECT payload FROM fire_fit_estado WHERE id = 1")
    if cur.fetchone() is None:
        cur.execute(
            "INSERT INTO fire_fit_estado (id, payload) VALUES (1, %s::jsonb)",
            (json.dumps(DEFAULT_STORE, ensure_ascii=False),),
        )
conn.commit()


def load_store():
url = _db_url()
if url and psycopg2 is not None:
    conn = None
    try:
        conn = psycopg2.connect(url)
        _garantir_tabela_pg(conn)
        with conn.cursor() as cur:
            cur.execute("SELECT payload FROM fire_fit_estado WHERE id = 1")
            row = cur.fetchone()
        if row and row[0] is not None:
            return normalizar_store(row[0])
        return normalizar_store(DEFAULT_STORE)
    except Exception:
        pass
    finally:
        if conn is not None:
            try:
                conn.close()
            except Exception:
                pass
if not os.path.exists(DADOS_JSON):
    inicial = normalizar_store(DEFAULT_STORE)
    save_store(inicial)
    return inicial
with open(DADOS_JSON, "r", encoding="utf-8") as f:
    try:
        bruto = json.load(f)
    except Exception:
        bruto = DEFAULT_STORE
return normalizar_store(bruto)


def save_store(store):
limpo = normalizar_store(store)
url = _db_url()
if url and psycopg2 is not None:
    conn = None
    try:
        conn = psycopg2.connect(url)
        _garantir_tabela_pg(conn)
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO fire_fit_estado (id, payload, atualizado_em) "
                "VALUES (1, %s::jsonb, CURRENT_TIMESTAMP) "
                "ON CONFLICT (id) DO UPDATE "
                "SET payload = EXCLUDED.payload, atualizado_em = CURRENT_TIMESTAMP",
                (json.dumps(limpo, ensure_ascii=False),),
            )
        conn.commit()
        return
    except Exception:
        pass
    finally:
        if conn is not None:
            try:
                conn.close()
            except Exception:
                pass
with open(DADOS_JSON, "w", encoding="utf-8") as f:
    json.dump(limpo, f, ensure_ascii=False, indent=2)


def obter_usuario_chave(payload=None):
cand = (
    request.args.get("usuario")
    or request.headers.get("X-Usuario")
    or ((payload or {}).get("usuario") if isinstance(payload, dict) else None)
)
if cand:
    return sanitizar_chave_usuario(cand)
store = load_store()
return store.get("usuario_ativo") or "eduardo"


def obter_data_usuario(store, chave, criar_se_faltar=True):
sk = sanitizar_chave_usuario(chave)
if sk not in store["usuarios"]:
    if not criar_se_faltar:
        sk = store.get("usuario_ativo") or "eduardo"
    else:
        store["usuarios"][sk] = normalizar_usuario_data({"perfil": {"nome": sk.capitalize()}}, sk)
return sk, store["usuarios"][sk]


def montar_resumo_dia(data):
pref = hoje_br_curto() + " "
alimentos_hoje = [x for x in data.get("alimentos", []) if str(x.get("data", "")).startswith(pref)]
treinos_hoje = [x for x in data.get("treinos", []) if str(x.get("data", "")).startswith(pref)]
balanca_hoje = [x for x in data.get("balanca", []) if str(x.get("data", "")).startswith(pref)]
glicemia_hoje = [x for x in data.get("glicemia", []) if str(x.get("data", "")).startswith(pref)]
base_vazia = criar_estado_vazio()
agua = data.get("agua", base_vazia["agua"])
objetivo = (data.get("perfil") or {}).get("objetivo", "perda")
kcal_total = sum(_to_int(x.get("kcal"), 0) for x in alimentos_hoje)
qtd_s = sum(1 for x in alimentos_hoje if x.get("saudavel", True))
qtd_ns = sum(1 for x in alimentos_hoje if not x.get("saudavel", True))
meta_kcal = max(200, _to_int(data.get("meta_kcal_dia"), 1500))
alerta_kcal = avaliar_calorias_dia(kcal_total, meta_kcal, objetivo, qtd_ns)
if not alimentos_hoje:
    av = "Nenhuma alimentação registrada hoje ainda."
elif qtd_ns == 0:
    av = "Alimentação do dia dentro do saudável."
elif qtd_s >= qtd_ns:
    av = "Boa base saudável hoje, com atenção aos itens extras."
else:
    av = "Atenção: maior parte dos itens de hoje é não saudável."
return {
    "data_hoje": agora_br_dt().strftime("%d/%m/%Y"),
    "agua_ml": _to_int(agua.get("consumido_ml"), 0),
    "meta_agua_ml": max(1, _to_int(agua.get("meta_ml"), 2500)),
    "agua_historico": agua.get("historico", []),
    "kcal_hoje": kcal_total,
    "meta_kcal_dia": meta_kcal,
    "alerta_kcal": alerta_kcal,
    "qtd_saudaveis": qtd_s,
    "qtd_nao_saudaveis": qtd_ns,
    "avaliacao_alimentacao": av,
    "alimentos_hoje": alimentos_hoje,
    "minutos_treino_hoje": sum(_to_int(x.get("duracao_min") or x.get("minutos"), 0) for x in treinos_hoje),
    "treinos_hoje": treinos_hoje,
    "destros_hoje": len(glicemia_hoje),
    "balanca_hoje": balanca_hoje,
}


@app.route("/")
def index():
return render_template("index.html")


@app.route("/api/estado", methods=["GET"])
def api_estado():
store = load_store()
req_user = request.args.get("usuario") or request.headers.get("X-Usuario")
chave = sanitizar_chave_usuario(req_user) if req_user else store.get("usuario_ativo", "eduardo")
if req_user and chave not in store["usuarios"]:
    store["usuarios"][chave] = normalizar_usuario_data({"perfil": {"nome": chave.capitalize()}}, chave)
    store["usuario_ativo"] = chave
    save_store(store)
elif req_user and store.get("usuario_ativo") != chave:
    store["usuario_ativo"] = chave
    save_store(store)

chave, data = obter_data_usuario(store, chave, criar_se_faltar=True)
peso, meta = _to_float(data.get("peso_atual"), None), _to_float(data.get("meta_peso"), None)
perfil = data.get("perfil", {})
meta_kcal = max(200, _to_int(data.get("meta_kcal_dia"), 1500))
usuarios_lista = [
    {"chave": k, "nome": (v.get("perfil") or {}).get("nome") or k.capitalize()}
    for k, v in store["usuarios"].items()
]
base_vazia = criar_estado_vazio()
return jsonify({
    "usuario_ativo": chave,
    "usuarios": usuarios_lista,
    "hora_servidor_br": agora_br_dt().strftime("%H:%M"),
    "perfil": perfil, "peso_atual": peso, "meta_peso": meta, "meta_kcal_dia": meta_kcal,
    "diferenca_meta": round(peso - meta, 1) if (peso is not None and meta is not None) else None,
    "orientacao": orientacao_instrutor(perfil, peso, meta, meta_kcal),
    "tabela_kcal_100g": TABELA_KCAL_100G,
    "agua": data.get("agua", base_vazia["agua"]),
    "refeicoes": data.get("refeicoes", DEFAULT_REFEICOES),
    "cardapio_semana": data.get("cardapio_semana", []),
    "balanca": data.get("balanca", []), "treinos": data.get("treinos", []),
    "glicemia": data.get("glicemia", []), "alimentos": data.get("alimentos", []),
    "resumo_dia": montar_resumo_dia(data),
})


@app.route("/api/perfil", methods=["POST"])
def api_perfil():
payload = request.get_json(force=True) or {}
store = load_store()
chave = obter_usuario_chave(payload)
chave, data = obter_data_usuario(store, chave, criar_se_faltar=True)
store["usuario_ativo"] = chave
perfil = data.setdefault("perfil", {})
if "nome" in payload:
    perfil["nome"] = str(payload.get("nome") or "").strip()
if "idade" in payload and payload.get("idade") not in (None, ""):
    perfil["idade"] = _to_int(payload.get("idade"), None)
if "altura_cm" in payload and payload.get("altura_cm") not in (None, ""):
    perfil["altura_cm"] = _to_float(payload.get("altura_cm"), None)
if payload.get("objetivo") in ("perda", "ganho"):
    perfil["objetivo"] = payload.get("objetivo")
if "meta_kcal_dia" in payload and payload.get("meta_kcal_dia") not in (None, ""):
    data["meta_kcal_dia"] = max(200, _to_int(payload.get("meta_kcal_dia"), 1500))
if "peso_atual" in payload and payload.get("peso_atual") not in (None, ""):
    p_val = _to_float(payload.get("peso_atual"), None)
    if p_val is not None:
        data["peso_atual"] = p_val
if "meta_peso" in payload and payload.get("meta_peso") not in (None, ""):
    m_val = _to_float(payload.get("meta_peso"), None)
    if m_val is not None:
        data["meta_peso"] = m_val
save_store(store)
return jsonify({"ok": True, "usuario_ativo": chave})


@app.route("/api/alimentos", methods=["POST"])
def api_add_alimento():
payload = request.get_json(force=True) or {}
store = load_store()
chave, data = obter_data_usuario(store, obter_usuario_chave(payload), criar_se_faltar=True)
store["usuario_ativo"] = chave
nome = str(payload.get("nome") or "").strip()
if not nome:
    return jsonify({"ok": False, "erro": "Informe o nome do alimento."}), 400
gramas = _to_float(payload.get("gramas") if payload.get("gramas") is not None else payload.get("quantidade"), None)
kcal_100g = _to_float(payload.get("kcal_100g"), None)
kcal = calcular_kcal_por_gramas(nome, gramas, kcal_100g, payload.get("kcal"))
registro = {
    "data": agora_br(), "nome": nome, "gramas": gramas,
    "kcal_100g": kcal_100g, "kcal": kcal,
    "saudavel": classificar_saude(nome, payload.get("saude_tipo")),
}
data.setdefault("alimentos", []).insert(0, registro)
save_store(store)
return jsonify({"ok": True, "item": registro, "resumo_dia": montar_resumo_dia(data)})


@app.route("/api/cardapio/prato", methods=["POST"])
def api_add_cardapio_prato():
payload = request.get_json(force=True) or {}
store = load_store()
chave, data = obter_data_usuario(store, obter_usuario_chave(payload), criar_se_faltar=True)
store["usuario_ativo"] = chave
dia = str(payload.get("dia") or "Segunda").strip()
if dia not in DIAS_SEMANA:
    dia = "Segunda"
refeicao = str(payload.get("refeicao") or "Almoço").strip() or "Almoço"
porcoes = []
for p in (payload.get("porcoes") or []):
    nome_p = str(p.get("alimento") or p.get("nome") or "").strip()
    if not nome_p:
        continue
    g_p = _to_float(p.get("gramas") if p.get("gramas") is not None else p.get("quantidade"), None)
    k100_p = _to_float(p.get("kcal_100g"), None)
    kcal_p = calcular_kcal_por_gramas(nome_p, g_p, k100_p, p.get("kcal"))
    porcoes.append({
        "alimento": nome_p, "gramas": g_p, "kcal_100g": k100_p,
        "kcal": kcal_p, "saudavel": classificar_saude(nome_p, p.get("saude_tipo")),
    })
if not porcoes:
    return jsonify({"ok": False, "erro": "Adicione ao menos um alimento ao prato."}), 400
total_kcal = sum(_to_int(x.get("kcal"), 0) for x in porcoes)
data.setdefault("cardapio_semana", []).append({
    "dia": dia, "refeicao": refeicao, "porcoes": porcoes, "total_kcal": total_kcal,
})
save_store(store)
return jsonify({"ok": True, "total_kcal": total_kcal})


@app.route("/api/cardapio/excluir/<int:idx>", methods=["DELETE"])
def api_del_cardapio(idx):
store = load_store()
chave, data = obter_data_usuario(store, obter_usuario_chave(), criar_se_faltar=False)
store["usuario_ativo"] = chave
lista = data.get("cardapio_semana", [])
if 0 <= idx < len(lista):
    lista.pop(idx)
    data["cardapio_semana"] = lista
    save_store(store)
return jsonify({"ok": True})


@app.route("/api/cardapio/consumir/<int:idx>", methods=["POST"])
def api_consumir_cardapio(idx):
store = load_store()
chave, data = obter_data_usuario(store, obter_usuario_chave(), criar_se_faltar=False)
store["usuario_ativo"] = chave
lista = data.get("cardapio_semana", [])
if 0 <= idx < len(lista):
    prato = lista[idx]
    refeicao = str(prato.get("refeicao") or "Refeição").strip()
    for p in (prato.get("porcoes") or []):
        nome_p = str(p.get("alimento") or p.get("nome") or "").strip()
        if not nome_p:
            continue
        g_p, k100_p = _to_float(p.get("gramas"), None), _to_float(p.get("kcal_100g"), None)
        kcal_p = calcular_kcal_por_gramas(nome_p, g_p, k100_p, p.get("kcal"))
        rotulo = f"{refeicao}: {nome_p}" if refeicao else nome_p
        data.setdefault("alimentos", []).insert(0, {
            "data": agora_br(), "nome": rotulo, "gramas": g_p,
            "kcal_100g": k100_p, "kcal": kcal_p, "saudavel": bool(p.get("saudavel", True)),
        })
    save_store(store)
return jsonify({"ok": True, "resumo_dia": montar_resumo_dia(data)})


@app.route("/api/agua", methods=["POST"])
def api_add_agua():
payload = request.get_json(force=True) or {}
store = load_store()
chave, data = obter_data_usuario(store, obter_usuario_chave(payload), criar_se_faltar=True)
store["usuario_ativo"] = chave
base_vazia = criar_estado_vazio()
agua = data.setdefault("agua", json.loads(json.dumps(base_vazia["agua"])))
agua["data_ref"] = hoje_br()
if "meta_ml" in payload and payload.get("meta_ml") not in (None, ""):
    agua["meta_ml"] = max(200, _to_int(payload.get("meta_ml"), 2500))
ml = _to_int(payload.get("ml"), 0)
if ml > 0:
    agua["consumido_ml"] = _to_int(agua.get("consumido_ml"), 0) + ml
    agua.setdefault("historico", []).insert(0, {"hora": agora_br_dt().strftime("%H:%M"), "ml": ml})
save_store(store)
return jsonify({"ok": True})


@app.route("/api/agua/excluir/<int:idx>", methods=["DELETE"])
def api_del_agua(idx):
store = load_store()
chave, data = obter_data_usuario(store, obter_usuario_chave(), criar_se_faltar=False)
store["usuario_ativo"] = chave
base_vazia = criar_estado_vazio()
agua = data.setdefault("agua", json.loads(json.dumps(base_vazia["agua"])))
hist = agua.get("historico", [])
if 0 <= idx < len(hist):
    removido = hist.pop(idx)
    agua["consumido_ml"] = max(0, _to_int(agua.get("consumido_ml"), 0) - _to_int(removido.get("ml"), 0))
    agua["historico"] = hist
    save_store(store)
return jsonify({"ok": True})


@app.route("/api/refeicoes", methods=["POST"])
def api_add_refeicao():
payload = request.get_json(force=True) or {}
store = load_store()
chave, data = obter_data_usuario(store, obter_usuario_chave(payload), criar_se_faltar=True)
store["usuario_ativo"] = chave
nome = str(payload.get("nome") or "Refeição").strip() or "Refeição"
horario = str(payload.get("horario") or "12:00").strip() or "12:00"
data.setdefault("refeicoes", []).append({"nome": nome, "horario": horario})
data["refeicoes"].sort(key=lambda x: x.get("horario", ""))
save_store(store)
return jsonify({"ok": True})


@app.route("/api/refeicoes/excluir/<int:idx>", methods=["DELETE"])
def api_del_refeicao(idx):
store = load_store()
chave, data = obter_data_usuario(store, obter_usuario_chave(), criar_se_faltar=False)
store["usuario_ativo"] = chave
lista = data.get("refeicoes", [])
if 0 <= idx < len(lista):
    lista.pop(idx)
    data["refeicoes"] = lista
    save_store(store)
return jsonify({"ok": True})


@app.route("/api/balanca", methods=["POST"])
def api_add_balanca():
payload = request.get_json(force=True) or {}
store = load_store()
chave, data = obter_data_usuario(store, obter_usuario_chave(payload), criar_se_faltar=True)
store["usuario_ativo"] = chave
peso = _to_float(payload.get("peso"), None)
if peso is None or peso <= 0:
    return jsonify({"ok": False, "erro": "Peso inválido."}), 400
meta = _to_float(payload.get("meta"), _to_float(data.get("meta_peso"), 75.0))
data["peso_atual"] = peso
if meta is not None and meta > 0:
    data["meta_peso"] = meta
data.setdefault("balanca", []).insert(0, {"data": agora_br(), "peso": peso, "meta": meta})
save_store(store)
return jsonify({"ok": True})


@app.route("/api/treinos", methods=["POST"])
def api_add_treino():
payload = request.get_json(force=True) or {}
store = load_store()
chave, data = obter_data_usuario(store, obter_usuario_chave(payload), criar_se_faltar=True)
store["usuario_ativo"] = chave
modalidade = str(payload.get("modalidade") or payload.get("tipo") or "Treino").strip()
duracao = max(1, _to_int(payload.get("duracao_min") or payload.get("minutos"), 30))
data.setdefault("treinos", []).insert(0, {
    "id": int(agora_br_dt().timestamp() * 1000), "data": agora_br(),
    "modalidade": modalidade, "duracao_min": duracao, "obs": str(payload.get("obs") or "").strip(),
})
save_store(store)
return jsonify({"ok": True})


@app.route("/api/treinos/<treino_id>", methods=["DELETE"])
def api_del_treino(treino_id):
store = load_store()
chave, data = obter_data_usuario(store, obter_usuario_chave(), criar_se_faltar=False)
store["usuario_ativo"] = chave
antes = len(data.get("treinos", []))
data["treinos"] = [t for t in data.get("treinos", []) if str(t.get("id")) != str(treino_id)]
if len(data["treinos"]) == antes:
    return jsonify({"erro": "Treino não encontrado."}), 404
save_store(store)
return jsonify({"ok": True})


@app.route("/api/glicemia", methods=["POST"])
def api_add_glicemia():
payload = request.get_json(force=True) or {}
store = load_store()
chave, data = obter_data_usuario(store, obter_usuario_chave(payload), criar_se_faltar=True)
store["usuario_ativo"] = chave
valor = _to_int(payload.get("valor"), 0)
if valor <= 0:
    return jsonify({"ok": False, "erro": "Valor de glicemia inválido."}), 400
data.setdefault("glicemia", []).insert(0, {
    "data": agora_br(), "valor": valor,
    "momento": str(payload.get("momento") or "Registro").strip() or "Registro",
})
save_store(store)
return jsonify({"ok": True})


@app.route("/api/excluir/<categoria>/<int:idx>", methods=["DELETE"])
def api_excluir_item(categoria, idx):
if categoria not in {"balanca", "treinos", "glicemia", "alimentos"}:
    return jsonify({"ok": False, "erro": "Categoria inválida."}), 400
store = load_store()
chave, data = obter_data_usuario(store, obter_usuario_chave(), criar_se_faltar=False)
store["usuario_ativo"] = chave
lista = data.get(categoria, [])
if 0 <= idx < len(lista):
    lista.pop(idx)
    data[categoria] = lista
    save_store(store)
return jsonify({"ok": True, "resumo_dia": montar_resumo_dia(data)})


if __name__ == "__main__":
app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 5001)))
