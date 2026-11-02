-- =============================================
-- 001_perfis.sql
-- Tabela de perfis + criação automática do perfil
-- =============================================

-- 1. Tabela de perfis: uma linha por usuário cadastrado
create table public.perfis (
  id         uuid primary key references auth.users (id) on delete cascade,
  nome       text,
  papel      text not null default 'associado'
             check (papel in ('associado', 'admin')),
  status     text not null default 'pendente'
             check (status in ('pendente', 'aprovado', 'recusado')),
  criado_em  timestamptz not null default now()
);

-- 2. Liga a proteção por linha (RLS)
alter table public.perfis enable row level security;

-- 3. Função que cria o perfil quando um usuário novo se cadastra
create function public.criar_perfil_novo_usuario()
returns trigger
language plpgsql
security definer
set search_path = ''
as $$
begin
  insert into public.perfis (id, nome)
  values (new.id, new.raw_user_meta_data ->> 'nome');
  return new;
end;
$$;

-- 4. Trigger: roda a função a cada novo usuário
create trigger ao_criar_usuario
  after insert on auth.users
  for each row execute function public.criar_perfil_novo_usuario();