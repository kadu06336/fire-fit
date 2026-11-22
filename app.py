import json
import os
from flask import Flask, jsonify, request
from dieta_routes import dieta_bp

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DADOS_PATH = os.path.join(BASE_DIR, "dados_fire_fit.json")

app = Flask(__name__, template_folder=os.path.join(BASE_DIR, "templates"), static_folder=BASE_DIR)
app.secret_key = os.environ.get("SECRET_KEY", "fire-fit-secret-key")
app.register_blueprint(dieta_bp)


def carregar_dados():
    if not os.path.exists(DADOS_PATH):
        dados_iniciais = {
            "treinos": [],
            "dieta_pratos": {
                "por_dia": {},
                "semanal": {"0": [], "1": [], "2": [], "3": [], "4": [], "5": [], "6": []},
            },
        }
        salvar_dados(dados_iniciais)
        return dados_iniciais

    with open(DADOS_PATH, "r", encoding="utf-8") as f:
        try:
            dados = json.load(f)
        except json.JSONDecodeError:
            dados = {}

    if not isinstance(dados, dict):
        dados = {}
    dados.setdefault("treinos", [])
    dados.setdefault(
        "dieta_pratos",
        {"por_dia": {}, "semanal": {"0": [], "1": [], "2": [], "3": [], "4": [], "5": [], "6": []}},
    )
    return dados


def salvar_dados(dados):
    with open(DADOS_PATH, "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)


def montar_estado(dados):
    return {
        "treinos": dados.get("treinos", []),
        "dieta_pratos": dados.get("dieta_pratos", {}),
    }


@app.route("/api/treinos/<treino_id>", methods=["DELETE"])
def api_del_treino(treino_id):
    dados = carregar_dados()
    antes = len(dados["treinos"])
    dados["treinos"] = [t for t in dados["treinos"] if str(t.get("id")) != str(treino_id)]
    if len(dados["treinos"]) == antes:
        return jsonify({"erro": "Treino não encontrado."}), 404
    salvar_dados(dados)
    return jsonify({"ok": True, "estado": montar_estado(dados)})


@app.route("/api/estado", methods=["GET"])
def api_estado():
    dados = carregar_dados()
    return jsonify({"ok": True, "estado": montar_estado(dados)})


@app.route("/api/estado", methods=["POST"])
def api_salvar_estado():
    payload = request.get_json(force=True) or {}
    dados = carregar_dados()
    if "treinos" in payload and isinstance(payload["treinos"], list):
        dados["treinos"] = payload["treinos"]
    if "dieta_pratos" in payload and isinstance(payload["dieta_pratos"], dict):
        dados["dieta_pratos"] = payload["dieta_pratos"]
    salvar_dados(dados)
    return jsonify({"ok": True, "estado": montar_estado(dados)})


if __name__ == "__main__":
    porta = int(os.environ.get("PORT", 5001))
    app.run(debug=True, host="0.0.0.0", port=porta)
