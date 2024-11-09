from flask import Flask, render_template, request, redirect, url_for, session
import random

app = Flask(__name__)
app.secret_key = 'uma_chave_secreta_aleatoria_e_segura'

personagem = {
    "nome": "",
    "raca": "Humano",
    "classe": "Guerreiro",
    "nivel": 1,
    "experiencia": 0,
    "atributos": {
        "forca": 1,
        "agilidade": 1,
        "inteligencia": 1,
        "carisma": 1,
        "sabedoria": 1
    },
    "status": {
        "ataque": 3,
        "defesa": 2,
        "vida": 9,
        "vida_max": 9,
        "esquiva": 2
    },
    "desafio": '', 
    "tentativas_bau": 3  
}

mimico = {
    "nome": "Mímico",
    "ataque": 6,
    "defesa": 2,
    "vida": 20,
    "vida_max": 20,
    "esquiva": 6
}

@app.route("/", methods=["GET", "POST"])
def criar_personagem():
    if request.method == "POST":
        personagem["nome"] = request.form["nome"]
        return redirect(url_for("menu"))
    return render_template("ficha.html", personagem=personagem)

@app.route("/menu", methods=["GET", "POST"])
def menu():
    if request.method == "POST":
        personagem["nome"] = request.form.get("nome", "Aventureiro")
        escolha = request.form.get("escolha")
        if escolha == "pousada":
            return redirect(url_for("pousada"))
        elif escolha == "caverna":
            return redirect(url_for("caverna"))

    # Redefinimos o valor de desafio_atual ao retornar ao menu
    session.pop('desafio_atual', None)
    return render_template("menu.html", personagem=personagem)

@app.route("/pousada")
def pousada():
    return render_template("pousada.html", personagem=personagem)

@app.route("/caverna", methods=["GET", "POST"])
def caverna():
    if 'tentativas' not in session:
        session['tentativas'] = 0

    desafio = random.randint(1, 8)
    resultado = {
        "titulo": "",
        "texto": ""
    }

    if desafio > 2:
        session['desafio_atual'] = 'monstros'
        resultado["titulo"] = "Desafio dos Monstros"
        resultado["texto"] = "Você encontrou monstros! Prepare-se para a batalha."

        if request.method == "POST":
            escolha = request.form["escolha"]
            if escolha == "voltar":
                session['tentativas'] = 0
                session.pop('desafio_atual', None)
                return redirect(url_for("menu"))
            elif escolha == "atacar":
                return redirect(url_for("combate"))
        return render_template("desafio.html", resultado=resultado, personagem=personagem)

    elif desafio <= 2:
        session['desafio_atual'] = 'bau'
        return redirect(url_for("desafio_bau"))

    return render_template("desafio.html", resultado=resultado, personagem=personagem)

@app.route("/desafio_bau", methods=["GET", "POST"])
def desafio_bau():
    if 'tentativas' not in session:
        session['tentativas'] = 0