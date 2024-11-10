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
        "ataque": 4,
        "defesa": 5,
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

monstro = {
    "nome": "Nome do Monstro",
    "nivel": 5,
    "status": {
        "ataque": 2,
        "defesa": 3,
        "vida": 12,
        "vida_max": 15,
        "esquiva": 8
    }
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

    session.pop('desafio_atual', None)
    return render_template("menu.html", personagem=personagem)

@app.route("/pousada")
def pousada():
    resultado = {
        "titulo": "",
        "texto": "Parabéns! Você alcançou a segurança da pousada. Aqui termina sua jornada por hoje."
    }
    return render_template("pousada.html", personagem=personagem, resultado=resultado)

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

    if 'sucesso' not in session:
        session['sucesso'] = False

    resultado = "" 
    sorteio = random.randint(1, 10)

    if sorteio <= 2:
        session['desafio_atual'] = "mimico"
        return redirect(url_for("combate_mimico"))
    
    if request.method == "POST":
        escolha = request.form["escolha"]

        if escolha == "abrir":
            if session['tentativas'] < 3 and not session['sucesso']:
                session['tentativas'] += 1
                sorteio = random.randint(1, 20)
                resultado = f"Tentativa {session['tentativas']} de 3: seu resultado foi {sorteio}. "

                if sorteio >= 10:
                    session['sucesso'] = True
                    resultado += "Boa! Você conseguiu abrir o baú e ganhou uma poção de vida."
                else:
                    resultado += "Infelizmente, não conseguiu abrir o baú. Tente novamente."

            if session['tentativas'] == 3 and not session['sucesso']:
                resultado += " Você atingiu o limite de tentativas. O baú permanece fechado."

        elif escolha == "voltar":
            session['tentativas'] = 0
            session['sucesso'] = False
            return redirect(url_for("menu"))

    return render_template("desafio_bau.html", resultado=resultado, tentativas=session['tentativas'], sucesso=session['sucesso'])


@app.route("/combate", methods=["GET", "POST"])
def combate():

    if 'monstro_vida' not in session:
        session['monstro_vida'] = monstro['status']['vida']
    if 'personagem_vida' not in session:
        session['personagem_vida'] = personagem['status']['vida']

    resultado = {
        "titulo": "Desafio dos Monstros",
        "texto": "Combate! Escolha atacar ou arrisque-se na fuga\n",
        "monstro_vida": session['monstro_vida'],
        "personagem_vida": session['personagem_vida']
    }

    if request.method == "POST":
        escolha = request.form["escolha"]

        if escolha == "voltar":
            rebote = random.randint(1, 3)
            if rebote == 1:
                resultado["texto"] = "O monstro te capturou"

            resetar_combate()
            return render_template("combate.html", resultado=resultado, personagem=personagem, monstro=monstro)

        if escolha == "atacar":
            mensagem_ataque = ""
            mensagem_retorno = ""

            if session["personagem_vida"] > 0:

        
                if random.randint(1, 100) > monstro['status']['esquiva']:
                    dano_personagem = personagem['status']['ataque'] * \
                        (1 - monstro['status']['defesa'] / 100)
                    session['monstro_vida'] -= round(dano_personagem)
                    session['monstro_vida'] = max(session['monstro_vida'], 0)
                    resultado['monstro_vida'] = session['monstro_vida']

                    if session['monstro_vida'] <= 0:
                        mensagem_ataque = "Você derrotou o monstro!"
                    else:
                        mensagem_ataque = f"Você atacou! Vida restante do monstro: {session['monstro_vida']}"
                else:
                    mensagem_ataque = "O monstro esquivou do seu ataque!"


               
                if session['monstro_vida'] > 0:
                    if random.randint(1, 100) > personagem['status']['esquiva']:
                        dano_monstro = monstro['status']['ataque'] * \
                            (1 - personagem['status']['defesa'] / 100)
                        session['personagem_vida'] -= round(dano_monstro)
                        session['personagem_vida'] = max(
                            session['personagem_vida'], 0)
                        resultado['personagem_vida'] = session['personagem_vida']

                        if session['personagem_vida'] <= 0:
                            mensagem_retorno = "O monstro te derrotou!"
                        else:
                            mensagem_retorno = f"O monstro atacou! Sua vida restante: {session['personagem_vida']}"
                    else:
                        mensagem_retorno = "Você esquivou do ataque do monstro!"

            
                resultado["texto"] = f"{mensagem_ataque}\n{mensagem_retorno}"

                return render_template("combate.html", resultado=resultado, personagem=personagem, monstro=monstro)

            else:
                resultado["texto"] = "você foi derrotado! Spawne de novo com um outro personagem"
                return render_template("pousada.html", resultado=resultado, personagem=personagem, monstro=monstro)

    return render_template("combate.html", resultado=resultado, personagem=personagem, monstro=monstro)


@app.route("/combate_mimico", methods=["GET", "POST"])
def combate_mimico():
    resultado = ""

    if request.method == "POST":
        escolha = request.form["escolha"]

        if escolha == "atacar":
            resultado = realizar_ataque(personagem, mimico)
        elif escolha == "defender":
            resultado = realizar_defesa(personagem, mimico)
        elif escolha == "esquivar":
            resultado = realizar_esquiva(personagem, mimico)
        elif escolha == "fugir":
            return redirect(url_for("menu"))

        if mimico["vida"] <= 0:
            resultado += "\nVocê derrotou o Mímico!"
        elif personagem["status"]["vida"] <= 0:
            resultado += "\nVocê foi derrotado pelo Mímico..."

    return render_template("combate_mimico.html", personagem=personagem, mimico=mimico, resultado=resultado)


def rolar_d20():
    return random.randint(1, 20)

def resetar_combate():
    session.pop('monstro_vida', None)
    session.pop('personagem_vida', None)
    return redirect(url_for("combate"))


def realizar_ataque(atacante, defensor):
    d20 = rolar_d20()
    ataque_valor = atacante["status"]["ataque"] if "status" in atacante else atacante["ataque"]
    defesa_valor = defensor["status"]["defesa"] if "status" in defensor else defensor["defesa"]

    resultado_ataque = d20 + ataque_valor
    if resultado_ataque >= defesa_valor:
        dano = (ataque_valor * 2) - \
            defesa_valor if d20 == 20 else ataque_valor - defesa_valor
        defensor["vida"] -= max(dano, 0)
        return f"Ataque bem-sucedido! {'Dano crítico! ' if d20 == 20 else ''}Causou {max(dano, 0)} de dano."
    else:
        return "O ataque falhou!"



def realizar_defesa(atacante, defensor):
    return f"{defensor['nome']} se preparou para defender, mas essa ação ainda não altera o combate atual."


def realizar_esquiva(atacante, defensor):
    d20 = rolar_d20()
    esquiva_valor = defensor["status"]["esquiva"] if "status" in defensor else defensor["esquiva"]
    ataque_valor = atacante["status"]["ataque"] if "status" in atacante else atacante["ataque"]

    resultado_esquiva = d20 + esquiva_valor
    if resultado_esquiva >= ataque_valor:
        return f"Esquiva bem-sucedida! {defensor['nome']} evitou o ataque!"
    else:
        dano = max(ataque_valor - defensor["status"]["defesa"],
                   0) if "status" in defensor else max(ataque_valor - defensor["defesa"], 0)
        defensor["vida"] -= dano
        return f"Esquiva falhou. Recebeu {dano} de dano."




if __name__ == "__main__":
    app.run(debug=True)
