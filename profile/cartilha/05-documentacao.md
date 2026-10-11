# Documentação: C4 e Scan Systems

[← Voltar ao catálogo da cartilha](../README.md)

A documentação segue o C4 model (skill `/c4-architecture`) e o Scan Systems (skill `/scan-systems`). As duas skills estão [publicadas aqui](https://github.com/Complexo-Industrial-Suape/.github/tree/main/skills), com instruções de instalação para o AGY e o Claude Code.

| Arquivo | Conteúdo | Obrigatório |
|---|---|---|
| `README.md` | O que o projeto faz, como rodar localmente em menos de 5 minutos e como rodar os testes | Sim |
| `docs/architecture/c4-context.md` | C4 nível 1: o sistema, quem usa e com quais sistemas externos ele conversa | Sim |
| `docs/architecture/c4-containers.md` | C4 nível 2: API, frontend, banco, filas e jobs, com a tecnologia de cada um e como se comunicam | Sim |
| `docs/architecture/c4-components-<parte>.md` | C4 nível 3: componentes internos, só para as partes complexas | Quando ajudar |
| `docs/architecture/c4-deployment.md` | Como o projeto deve rodar em produção, ou seja, o que você espera do GCP | Recomendado |
| `docs/systems/<nome-do-projeto>.md` | Relatório do Scan Systems: stack, modelos de dados, rotas da API, variáveis de ambiente e segredos (só os nomes), fluxos de acesso, testes e segurança | Sim |
| `docs/SYSTEMS_CATALOG.md` | Catálogo consolidado do Scan Systems | Sim |

Algumas regras:
- Os diagramas usam Mermaid e precisam renderizar no GitHub.
- Todo elemento do diagrama tem nome, tecnologia e descrição. Toda seta diz o que faz e por qual protocolo, como "Consulta reservas via HTTPS/JSON". Rótulo genérico como "usa" não serve.
- Nada inventado. Cada afirmação aponta para um arquivo real do repositório, com link relativo, e nunca para um caminho da sua máquina (`C:\Users\...`, `/home/...`).
- Liste todas as variáveis de ambiente e segredos que o projeto usa, só com os nomes. Os segredos do GCP são criados a partir dessa lista.

**Documentação ausente ou incompleta bloqueia o provisionamento.** Isso vale para um arquivo obrigatório que falta, uma seção que falta (o README sem como rodar os testes, por exemplo) e uma variável que o código lê e a documentação não cita. Documentação desatualizada vira issue, mas não bloqueia.

No AGY ou no Claude Code, peça "rode /scan-systems neste repositório" e depois "/c4-architecture". Revise o resultado antes de commitar: quem responde pela documentação é você, não a ferramenta.
