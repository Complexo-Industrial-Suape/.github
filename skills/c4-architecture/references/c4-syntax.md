# Mermaid C4 que renderiza no GitHub

Carregue no passo 3 do SKILL.md. Não carregue para o inventário.

## Elementos

```
Person(alias, "Nome", "Descrição")
Person_Ext(alias, "Nome", "Descrição")
System(alias, "Nome", "Descrição")
System_Ext(alias, "Nome", "Descrição")
SystemDb_Ext(alias, "Nome", "Descrição")
Container(alias, "Nome", "Tecnologia", "Descrição")
ContainerDb(alias, "Nome", "Tecnologia", "Descrição")
ContainerQueue(alias, "Nome", "Tecnologia", "Descrição")
Container_Ext(alias, "Nome", "Tecnologia", "Descrição")
Component(alias, "Nome", "Tecnologia", "Descrição")
System_Boundary(alias, "Nome") { ... }
Container_Boundary(alias, "Nome") { ... }
Deployment_Node(alias, "Nome", "Tipo", "Descrição") { ... }
Rel(origem, destino, "Ação", "Protocolo")
UpdateLayoutConfig($c4ShapeInRow="3", $c4BoundaryInRow="1")
UpdateRelStyle(origem, destino, $offsetY="-20")
```

`Person` e `System*` não têm campo de tecnologia. Ponha a tecnologia na descrição: `System_Ext(gemini, "Gemini API", "Google, HTTPS/JSON. Gera resumo da inspeção")`.

## O que quebra ou fica ruim no GitHub

O GitHub usa uma versão do Mermaid em que o C4 ainda é experimental. Na prática:

| Problema | O que fazer |
|---|---|
| Aspas duplas dentro de rótulo encerram a string e quebram o diagrama | Use aspas simples ou reescreva |
| `(`, `)` e `,` dentro de rótulo sem aspas | Sempre rótulos entre aspas duplas |
| Acentos funcionam, mas `<br>` e HTML aparecem literais ou somem | Rótulo curto, uma linha |
| `BiRel` | Não use: deixa ambíguo quem inicia. Duas `Rel` se precisar |
| `Rel_U/D/L/R` às vezes ignorados | Não dependa deles; ajuste com `UpdateLayoutConfig` |
| Rótulos de seta sobrepostos | `UpdateRelStyle(a, b, $offsetY="-20")` |
| `$tags`, `AddElementTag`, `SHOW_LEGEND()`, sprites | Não suportados: renderizam sem efeito ou quebram. Para marcar outro provedor use o texto "[FORA DO GCP]" no nome e `UpdateElementStyle(alias, $bgColor="#b00020")` |
| Alias com hífen ou começando com número | Alias em camelCase: `apiChamados` |
| Mais de ~15 elementos | Layout ilegível. Divida (ex.: um c4-components por parte) |
| Bloco declarado como ```mermaid com indentação errada de chaves | Cada `{` fecha com `}` em linha própria |

Se o C4 não renderizar mesmo depois disso, é aceitável usar `flowchart LR` com o mesmo conteúdo (nome, tecnologia e descrição no rótulo do nó; ação + protocolo na seta). Diga no arquivo que é C4 nível N em flowchart.

## Validar sem navegador

Quando o `mermaid-cli` falha por falta de Chrome/puppeteer, use o parser oficial com jsdom. Ele confirma a sintaxe (não desenha):

```bash
T=$(mktemp -d) && cd "$T" && npm i --silent mermaid@11 jsdom
cat > check.mjs <<'EOF'
import {JSDOM} from 'jsdom'; import fs from 'fs';
const d=new JSDOM('<body></body>'); globalThis.window=d.window; globalThis.document=d.window.document;
Object.defineProperty(globalThis,'navigator',{value:d.window.navigator}); globalThis.DOMParser=d.window.DOMParser;
const {default:m}=await import('mermaid'); m.initialize({startOnLoad:false});
for (const f of process.argv.slice(2)) for (const [,b] of fs.readFileSync(f,'utf8').matchAll(/```mermaid\n([\s\S]*?)```/g))
  try { const r=await m.parse(b); console.log('OK', f, r.diagramType) } catch(e) { console.log('ERRO', f, String(e.message).split('\n')[0]); process.exitCode=1 }
EOF
node check.mjs /caminho/do/repo/docs/architecture/*.md
```

Registre no relatório ao dev que a sintaxe foi validada, mas a renderização no GitHub não.

## Protocolos usuais em Suape

HTTPS/JSON (web→api, api→APIs externas), SQL/TCP 5432 (PostgreSQL no Cloud SQL), conector Cloud SQL via socket Unix, MongoDB wire/TCP 27017, API do GCS via HTTPS, SMTP/TLS 587, OAuth 2.0/OIDC (login Google institucional), Cloud Scheduler → HTTPS POST com OIDC (cron).
