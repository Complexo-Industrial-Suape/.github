# Repositório: org, nome e segredos

[← Voltar ao catálogo da cartilha](../README.md)

O pedido de ambiente só segue quando todos os itens abaixo estiverem atendidos.

- [ ] Está na org Complexo-Industrial-Suape, e não na sua conta pessoal. Todo desenvolvedor da Coordenadoria pode criar repositórios lá.
- [ ] O nome está em kebab-case: letras minúsculas, números e hífen, sem `_`, `.` ou maiúsculas. O formato é `<produto>[-api|-web|-mobile]`, como `rdo-suape-api`, `suape-drive` ou `premio-inova-industria-web`. "Suape" entra no nome quando faz parte do produto.
- [ ] O código do MVP está na `main`. Não precisa criar `dev` nem `hml`, porque elas são criadas no provisionamento. Se já existirem, serão aproveitadas.
- [ ] Nenhum segredo foi commitado: senha, token, chave de API, `.env` com valores reais ou chave de service account. No repositório fica só o `.env.example`, com os nomes das variáveis e sem valores.
- [ ] Os assets da marca Suape que o projeto usa (logos, fontes, cores) estão copiados numa pasta do próprio projeto, como `web/public/brand/`. Se você clonar o `suape-brand` dentro do repositório para consultar o kit, ponha a pasta `suape-brand/` no `.gitignore`. Nunca commite o kit inteiro e nunca use o `suape-brand` como submódulo.
- [ ] Todos os commits do repositório estão assinados e aparecem como **Verified** no GitHub. Veja [Autenticação e assinatura com chave SSH](01-chave-ssh-autenticacao-e-assinatura.md).
