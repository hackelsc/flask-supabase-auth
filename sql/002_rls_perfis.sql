-- =============================================
-- 002_rls_perfis.sql
-- Regras de acesso da tabela perfis
-- =============================================

-- 1. Libera a tabela para usuários logados (1ª camada: quais tabelas e colunas)
grant select on public.perfis to authenticated;
grant update (nome) on public.perfis to authenticated;

-- 2. Função que responde: quem está logado é admin aprovado?
create function public.eh_admin()
returns boolean
language sql
stable
security definer
set search_path = ''
as $$
  select exists (
    select 1
    from public.perfis
    where id = auth.uid()
      and papel = 'admin'
      and status = 'aprovado'
  );
$$;

-- 3. Regras de linha (2ª camada: quais linhas)
create policy "ver o próprio perfil"
  on public.perfis for select
  to authenticated
  using (id = auth.uid());

create policy "admin vê todos os perfis"
  on public.perfis for select
  to authenticated
  using (public.eh_admin());

create policy "editar o próprio perfil"
  on public.perfis for update
  to authenticated
  using (id = auth.uid())
  with check (id = auth.uid());

-- 4. Função do admin para mudar papel e status
create function public.admin_atualizar_perfil(alvo uuid, novo_papel text, novo_status text)
returns void
language plpgsql
security definer
set search_path = ''
as $$
begin
  if not public.eh_admin() then
    raise exception 'Apenas administradores podem alterar papel e status.';
  end if;

  update public.perfis
  set papel = novo_papel,
      status = novo_status
  where id = alvo;
end;
$$;

-- 5. Só usuários logados podem chamar a função do admin
revoke execute on function public.admin_atualizar_perfil(uuid, text, text) from public, anon;
grant execute on function public.admin_atualizar_perfil(uuid, text, text) to authenticated;