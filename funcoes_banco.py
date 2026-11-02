import os

from flask import session
from supabase import create_client


def novo_cliente():
    return create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_KEY"])


def cliente_logado():
    cliente = novo_cliente()
    cliente.postgrest.auth(session["access_token"])
    return cliente


def buscar_meu_perfil():
    resposta = (
        cliente_logado()
        .table("perfis")
        .select("nome, papel, status")
        .eq("id", session["usuario_id"])
        .execute()
    )
    return resposta.data[0]

def listar_perfis():
    resposta = (
        cliente_logado()
        .table("perfis")
        .select("id, nome, papel, status, criado_em")
        .order("criado_em")
        .execute()
    )
    return resposta.data

def atualizar_perfil(alvo, novo_papel, novo_status):
    cliente_logado().rpc("admin_atualizar_perfil", {
        "alvo": alvo,
        "novo_papel": novo_papel,
        "novo_status": novo_status,
    }).execute()