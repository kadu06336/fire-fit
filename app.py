import json
import os
from datetime import datetime
from flask import Flask, jsonify, render_template, request

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE_DIR, "dados_fire_fit.json")

app = Flask(__name__, template_folder=BASE_DIR)


def load_data():
    default = {
        "perfil": {
            "nome": "",
            "idade": None,
            "altura_cm": None,
            "objetivo": "perda"
        },
        "meta_peso": 75.0,
        "peso_atual": None,
        "balanca": [],
        "treinos": [],
        "glicemia": [],
        "prato": [],
        "alimentos": [
            {"nome": "Arroz integral (100g)", "kcal": 124},
            {"nome": "Peito de frango grelhado (100g)", "kcal": 159},
            {"nome": "Ovo cozido (1 un)", "kcal": 78},
            {"nome": "Banana prata (1 un)", "kcal": 87}
        ]
    }
    if not os.path.exists(DATA_FILE):
        save_data(default)
        return default
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        for k, v in default.items():
            if k not in data:
                data[k] = v
        if isinstance(data.get("perfil"), dict):
            for pk, pv in default["perfil"].items():
                if pk not in data["perfil"]:
                    data["perfil"][pk] = pv
        return data
    except Exception:
        return default


def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


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
        "perfil": perfil,
        "peso_atual": peso,
        "meta_peso": meta,
        "diferenca_meta": diferenca,
        "orientacao": orientacao_instrutor(perfil, peso, meta),
        "balanca": data.get("balanca", []),
        "treinos": data.get("treinos", []),
        "glicemia": data.get("glicemia", []),
        "prato": data.get("prato", []),
        "alimentos": data.get("alimentos", [])
    })


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

    if "meta_peso" in payload and payload.get("meta_peso") not in (None, ""):
        data["meta_peso"] = float(payload.get("meta_peso"))

    if "peso_atual" in payload and payload.get("peso_atual") not in (None, ""):
        peso_val = float(payload.get("peso_atual"))
        data["peso_atual"] = peso_val
        data["balanca"].insert(0, {
            "data": datetime.now().strftime("%d/%m %H:%M"),
            "peso": peso_val,
            "meta": data["meta_peso"]
        })

    data["perfil"] = perfil
    save_data(data)
    return jsonify({"ok": True})


@app.route("/api/meta-peso", methods=["POST"])
def salvar_meta_peso():
    payload = request.get_json(force=True) or {}
    data = load_data()
    if "meta_peso" in payload and payload["meta_peso"] not in (None, ""):
        data["meta_peso"] = float(payload["meta_peso"])
    if "peso_atual" in payload and payload["peso_atual"] not in (None, ""):
        peso_val = float(payload["peso_atual"])
        data["peso_atual"] = peso_val
        data["balanca"].insert(0, {
            "data": datetime.now().strftime("%d/%m %H:%M"),
            "peso": peso_val,
            "meta": data["meta_peso"]
        })
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
        "data": datetime.now().strftime("%d/%m %H:%M"),
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
        "data": datetime.now().strftime("%d/%m %H:%M"),
        "descricao": str(payload.get("descricao", "")).strip(),
        "minutos": int(payload.get("minutos", 0) or 0)
    })
    save_data(data)
    return jsonify({"ok": True})


@app.route("/api/glicemia", methods=["POST"])
def add_glicemia():
    payload = request.get_json(force=True) or {}
    data = load_data()
    data["glicemia"].insert(0, {
        "data": datetime.now().strftime("%d/%m %H:%M"),
        "valor": float(payload.get("valor", 0) or 0),
        "momento": str(payload.get("momento", "Registro")).strip()
    })
    save_data(data)
    return jsonify({"ok": True})


@app.route("/api/prato", methods=["POST"])
def add_prato():
    payload = request.get_json(force=True) or {}
    data = load_data()
    data["prato"].insert(0, {
        "data": datetime.now().strftime("%d/%m %H:%M"),
        "item": str(payload.get("item", "")).strip(),
        "kcal": int(payload.get("kcal", 0) or 0)
    })
    save_data(data)
    return jsonify({"ok": True})


@app.route("/api/alimentos", methods=["POST"])
def add_alimento():
    payload = request.get_json(force=True) or {}
    data = load_data()
    data["alimentos"].insert(0, {
        "nome": str(payload.get("nome", "")).strip(),
        "kcal": int(payload.get("kcal", 0) or 0)
    })
    save_data(data)
    return jsonify({"ok": True})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
