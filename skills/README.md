# Skills de documentação de Suape

Skills usadas para documentar os projetos da Coordenadoria antes do provisionamento no GCP, conforme a [Cartilha de Desenvolvimento de Suape](../profile/README.md).

| Skill | Para que serve |
|---|---|
| [`c4-architecture`](c4-architecture/SKILL.md) | Gera os diagramas C4 (contexto, contêineres, componentes, deployment) em Mermaid, em `docs/architecture/` |
| [`scan-systems`](scan-systems/SKILL.md) | Audita o projeto e gera o relatório `docs/systems/<projeto>.md` e o `docs/SYSTEMS_CATALOG.md` |

As demais pastas são skills de apoio que o `scan-systems` carrega durante a varredura: modelagem de banco, contrato de API, diagramas, segredos, dependências, SQL injection, cabeçalhos HTTP e revisão de texto. Instale a pasta inteira.

## Instalação

Clone este repositório e copie a pasta `skills/` para o diretório de skills da sua ferramenta.

```bash
git clone https://github.com/Complexo-Industrial-Suape/.github.git suape-github
```

**AGY (Antigravity)**
```bash
mkdir -p ~/.gemini/config/skills
cp -r suape-github/skills/* ~/.gemini/config/skills/
```

**Claude Code**
```bash
mkdir -p ~/.claude/skills
cp -r suape-github/skills/* ~/.claude/skills/
```

No Windows, copie as pastas para `%USERPROFILE%\.gemini\config\skills\` (AGY) ou `%USERPROFILE%\.claude\skills\` (Claude Code).

## Uso

Na raiz do seu repositório, peça à ferramenta:

1. `rode /scan-systems neste repositório`
2. `rode /c4-architecture e gere os diagramas de contexto e contêineres`

Revise o resultado antes de commitar: você responde pela documentação do seu projeto.

## Créditos e licença

Skills criadas por [Raul César](https://github.com/RaulCsar) para a [Mangue House](https://github.com/mangue-house) e adaptadas para a CTIC de Suape. `scan-systems` e `c4-architecture` foram reescritas para as regras da cartilha e testadas em um projeto real de Suape. Licença MIT (ver [LICENSE](LICENSE)).
