import os

from dotenv import load_dotenv
from flask import Flask, flash, redirect, render_template, request, session, url_for
from supabase_auth.errors import AuthApiError
from funcoes_banco import atualizar_perfil, buscar_meu_perfil, cliente_logado, listar_perfis, novo_cliente

load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ["FLASK_SECRET_KEY"]


@app.route("/")
def inicio():
    return render_template("inicio.html")

@app.route("/paineis")
def paineis():
    return render_template("paineis.html")

@app.route("/teste-conexao")
def teste_conexao():
    try:
        resposta = novo_cliente().table("perfis").select("nome").execute()
        return f"Conectou. Linhas visíveis: {resposta.data}"
    except Exception as erro:
        return f"Conectou, mas o banco recusou: {erro}"

@app.route("/cadastro", methods=["GET", "POST"])
def cadastro():
    if request.method == "POST":
        nome = request.form["nome"]
        email = request.form["email"]
        senha = request.form["senha"]

        try:
            novo_cliente().auth.sign_up({
                "email": email,
                "password": senha,
                "options": {"data": {"nome": nome}},
            })
            flash("Cadastro feito. Aguarde a aprovação do administrador.")
            return redirect(url_for("inicio"))
        except Exception as erro:
            flash(f"Não foi possível cadastrar: {erro}")

    return render_template("cadastro.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        senha = request.form["senha"]

        try:
            resposta = novo_cliente().auth.sign_in_with_password({
                "email": email,
                "password": senha,
            })
            session["access_token"] = resposta.session.access_token
            session["usuario_id"] = resposta.user.id
            session["papel"] = buscar_meu_perfil()["papel"]
            flash("Login feito.")
            return redirect(url_for("inicio"))
        except AuthApiError as erro:
            if erro.code == "email_not_confirmed":
                flash("Seu e-mail ainda não foi confirmado. Verifique sua caixa de entrada.")
            else:
                flash("E-mail ou senha incorretos.")
        except Exception:
            session.clear()
            flash("Não foi possível entrar. Tente de novo.")

    return render_template("login.html")

@app.route("/perfil")
def meu_perfil():
    if "access_token" not in session:
        flash("Faça login para ver o seu perfil.")
        return redirect(url_for("login"))

    try:
        perfil = buscar_meu_perfil()
    except Exception:
        session.clear()
        flash("Sua sessão expirou. Faça login de novo.")
        return redirect(url_for("login"))

    return render_template("perfil.html", perfil=perfil)

@app.route("/logout")
def logout():
    session.clear()
    flash("Você saiu.")
    return redirect(url_for("inicio"))

@app.route("/area-restrita")
def area_restrita():
    if "access_token" not in session:
        flash("Faça login para acessar a área restrita.")
        return redirect(url_for("login"))

    try:
        perfil = buscar_meu_perfil()
    except Exception:
        session.clear()
        flash("Sua sessão expirou. Faça login de novo.")
        return redirect(url_for("login"))

    if perfil["status"] != "aprovado":
        flash("Seu cadastro ainda não foi aprovado pelo administrador.")
        return redirect(url_for("meu_perfil"))

    return render_template("area_restrita.html", perfil=perfil)

@app.route("/admin")
def admin():
    if "access_token" not in session:
        flash("Faça login para acessar a administração.")
        return redirect(url_for("login"))

    try:
        perfil = buscar_meu_perfil()
    except Exception:
        session.clear()
        flash("Sua sessão expirou. Faça login de novo.")
        return redirect(url_for("login"))

    if perfil["papel"] != "admin" or perfil["status"] != "aprovado":
        flash("Esta página é só para administradores.")
        return redirect(url_for("inicio"))

    perfis = listar_perfis()
    return render_template("admin.html", perfis=perfis)

@app.route("/admin/atualizar", methods=["POST"])
def admin_atualizar():
    if "access_token" not in session:
        flash("Faça login para acessar a administração.")
        return redirect(url_for("login"))

    try:
        atualizar_perfil(
            request.form["alvo"],
            request.form["papel"],
            request.form["status"],
        )
        flash("Perfil atualizado.")
    except Exception as erro:
        flash(f"Não foi possível atualizar: {erro}")

    return redirect(url_for("admin"))

if __name__ == "__main__":
    app.run(debug=True)