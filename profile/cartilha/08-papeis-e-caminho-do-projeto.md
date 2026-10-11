# Papéis e caminho de um projeto novo

[← Voltar ao catálogo da cartilha](../README.md)

## Quem faz o quê

| Você, desenvolvedor | Responsável pela infraestrutura (Raul César) |
|---|---|
| Cria o repositório na org | Administra a org do GitHub, o GCP e o AGY |
| Desenvolve o MVP e as regras de negócio | Avalia o pedido e confere a documentação |
| Documenta o projeto (C4 + Scan Systems) | Cria os três ambientes e as branches `dev` e `hml` |
| Deixa o projeto dockerizado e com testes | Configura o deploy automático (Cloud Build) |
| Controla branches, PRs e a promoção entre ambientes | Combina com você CI, ciclos, rotinas e cron jobs |
| Corrige o que for apontado nas issues | Devolve um resumo do que foi feito |

A infraestrutura não mexe em regra de negócio. Se algo no código impedir o deploy, você recebe uma issue no repositório e faz a correção.

Para trabalhar aqui, você precisa dominar o básico de Git e GitHub: branch, commit, PR, merge e resolução de conflito. E precisa pensar desde o início em duas coisas: como o projeto se comporta com mais usuários e quanto custa mantê-lo no ar.

## O caminho de um projeto novo

```
1. Você cria o repositório e desenvolve o MVP
2. Você documenta (C4 + Scan Systems) e sobe tudo para o GitHub, com commits assinados
3. Você abre o chamado por e-mail
4. A infraestrutura confirma, confere a documentação e inspeciona o projeto
     └─ faltou algo? → issues no repositório + resposta no e-mail → você corrige → volta ao passo 4
5. A infraestrutura cria os ambientes, as branches e o deploy automático
6. Vocês alinham CI, ciclos, rotinas e cron jobs
7. Você recebe o resumo e passa a trabalhar no fluxo normal
```

> **Projeto sem documentação não recebe ambiente no GCP.** Não há exceção.

Detalhes de cada etapa: [repositório](03-repositorio.md), [pronto para o GCP](04-pronto-para-o-gcp.md), [documentação](05-documentacao.md) e [chamado de provisionamento](06-chamado-de-provisionamento.md).
