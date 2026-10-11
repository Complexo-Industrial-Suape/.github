# Marca e Identidade Visual: Suape Brand Kit

[← Voltar ao catálogo da cartilha](../README.md)

A identidade visual é patrimônio público e institucional do Complexo Industrial Portuário de Suape. Todo sistema desenvolvido pela Coordenadoria de Inovação e hospedado no Google Cloud deve seguir com fidelidade absoluta as diretrizes estabelecidas pela **CCOM (Coordenadoria de Comunicação)**, consolidadas no Manual de Identidade Visual de Suape e implementadas no repositório [suape-brand](https://github.com/Complexo-Industrial-Suape/suape-brand).

---

## 1. Princípio fundamental: "Não reescreva a marca. Importe-a."

A marca gráfica de Suape é composta por relações geométricas precisas, curvas de Bézier calibradas e proporções homologadas pela CCOM.

* **Nunca redesenhe nem copie paths SVG manualmente:** Copiar coordenadas vetoriais à mão para dentro de componentes JSX gera pequenas deformações acumuladas que desfiguram o símbolo oficial.
* **Use os arquivos vetoriais oficiais:** Utilize os arquivos SVG originais mantidos no [suape-brand](https://github.com/Complexo-Industrial-Suape/suape-brand) ou os componentes prontos (`<SuapeLogo />`, `<MarcaAnimada />`).

---

## 2. A Splash Screen é obrigatória em todos os sistemas

A tela de abertura oficial animada (**splash screen**) deve ser exibida no carregamento de **todos os sistemas desenvolvidos por Suape**.

### Por que a splash screen é obrigatória?
* **Assinatura institucional:** Garante ao servidor, operador portuário ou cidadão a certeza imediata de que está acessando um software oficial e auditado do Complexo de Suape.
* **Padronização da experiência:** Unifica a identidade visual de todos os sistemas sob a mesma linguagem visual e de transição.

### Regras estritas de exibição da Splash Screen
1. **Fundo branco obrigatório (`#FFFFFF`):** A assinatura oficial ocorre sempre sobre fundo branco. Não use fundos escuros ou coloridos na abertura.
2. **Marca nas cores originais:** As peças caem e se encaixam exibindo o azul e o amarelo oficiais.
3. **Legenda institucional padronizada:** O texto animado deve dizer exatamente:
   * Título: `SUAPE`
   * Subtítulo: `COORDENADORIA DE INOVAÇÃO`
4. **Exibição uma única vez por sessão (`umaVezPorSessao`):**
   * A animação tem duração de ~2,9 segundos (estilo oficial *caindo*).
   * Ela **nunca** deve rodar a cada troca de rota ou refresh acidental. Configure para gravar no `sessionStorage` e rodar apenas no primeiro acesso daquela sessão do navegador.
5. **Acessibilidade (`prefers-reduced-motion`):**
   * Usuários com sensibilidade vestibular que configuram redução de movimento no sistema operacional não devem receber a animação física: o componente detecta a preferência e exibe a marca já montada instantaneamente.

### Como implementar a Splash Screen

#### Em aplicações React / Vite
Utilize o componente oficial do kit:
```tsx
import { MarcaAnimada } from "./components/brand/MarcaAnimada";

export function App() {
  return (
    <>
      <MarcaAnimada 
        variante="tela-cheia" 
        umaVezPorSessao={true} 
      />
      <MinhaAplicacao />
    </>
  );
}
```

#### Em aplicações Vanilla JS / HTML
```html
<div id="suape-splash"></div>
<script src="/brand/vanilla/suape-splash.js"></script>
<script>
  SuapeSplash.iniciar({
    umaVezPorSessao: true
  });
</script>
```

---

## 3. Diretrizes da CCOM para Logotipos Vetorizados

### Os formatos homologados

| Formato | Arquivo oficial | Proporção | Onde usar |
|---|---|---|---|
| **Horizontal** | `assets/logos/logo-horizontal.svg` | 733,91 × 309,1 | **Padrão oficial.** Cabeçalhos principais, barras de navegação, relatórios e rodapés. |
| **Quadrado (CIN)** | `assets/logos/logo-quadrado-cin.svg` | 463,5 × 463,37 | Espaços restritos, avatares de perfil, ícones de aplicativo (PWA/Favicon) e telas móveis. |
| **Isotipo isolado** | `assets/logos/isotipo.svg` | Proporcional | Apenas quando o espaço for menor que o tamanho mínimo da logo completa. |

### Área de Respiro (Área de Proteção)
Em volta de qualquer aplicação da logo, reserve obrigatoriamente uma margem livre igual à **altura do sol central** (cerca de 1/4 da altura do isotipo). 
* **Regra:** Nenhum texto, borda, botão, ícone ou elemento gráfico pode invadir essa área.

### Tamanhos mínimos em tela
* **Logo Horizontal:** Largura mínima de **120 px**.
* **Logo Quadrada:** Largura mínima de **40 px**.
* *Abaixo dessas dimensões, os detalhes do sol e as curvas dos polígonos perdem definição.*

### Aplicação sobre fundos escuros ou azuis
Quando a logo for aplicada sobre o azul institucional (`#3257A4`) ou sobre fundos com luminosidade escura:
* **Aplicação monocromática branca obrigatória:** A logo deve ser renderizada 100% branca (em React: `<SuapeLogo monocromatica />` ou classe `.suape-em-azul`).
* **Proibição:** Nunca aplique a logo colorida sobre fundo azul: o azul da marca se funde com o fundo e a visibilidade é destruída.

### O que NUNCA fazer com a logo (Manual CCOM)
* **Nunca distorcer proporções:** Proibido esticar apenas na largura ou comprimir na altura. Mantenha sempre proporção fixa (`preserveAspectRatio="xMidYMid meet"`).
* **Nunca aplicar gradientes, sombras ou relevos:** A marca de Suape é vetorial plana (flat design).
* **Nunca alterar as cores:** Não invente variações cinzas, verdes ou tons fora da paleta oficial.
* **Nunca redigitar "SUAPE":** A tipografia do logotipo não é um texto com fonte comum; são curvas vetoriais específicas e homologadas.
* **Nunca rotacionar:** A logo não deve ser inclinada nem rotacionada em telas ou impressos.

---

## 4. Paleta de Cores e Acessibilidade (Tokens)

A identidade visual utiliza duas cores estruturais:

| Cor | Hexadecimal | Variável CSS | Função |
|---|---|---|---|
| **Azul Institucional** | `#3257A4` | `--suape-azul` | Cor dominante. Estrutura de interface, barras superiores, botões primários e links. |
| **Amarelo Inovação** | `#FAB400` | `--suape-amarelo` | Cor de acento. Destaques pontuais, sol central da marca e badges. |

### Regra de Ouro do Contraste (WCAG AA / AAA)
* **Azul Institucional (`#3257A4`):** Possui contraste superior a **7.4:1** com texto branco. Passa com folga no critério AAA. Pode ser usado com texto branco sem restrições.
* **Amarelo Inovação (`#FAB400`):** O contraste de texto branco sobre amarelo é de apenas **1.9:1**, sendo **gravemente reprovado** nos testes de acessibilidade.
  * **Regra obrigatória:** Sobre fundos amarelos, o texto deve ser **sempre escuro** (`#1f1400` ou `#000000`).
  * **O amarelo é acento:** Não utilize amarelo como cor de fundo de seções inteiras ou barras de navegação.

---

## 5. Tipografia Oficial: Família Matt

A fonte tipográfica oficial de Suape é a **Matt**.

* **Pesos homologados:** 400 (Regular) e 700 (Bold), além de suas variações itálicas.
* **Atenção:** A família não possui pesos 500 (Medium) ou 600 (Semi-bold). Não defina esses valores no CSS, pois os navegadores sintetizam distorções artificiais dos glifos.
* **Rótulos institucionais:** Categorias, tags e chamadas institucionais devem ser grafadas em caixa alta com espaçamento entre letras expandido:
  ```html
  <span class="suape-rotulo">COORDENADORIA DE INOVAÇÃO</span>
  ```

---

## 6. Como integrar o kit no repositório do seu projeto

Para manter o repositório leve e garantir deploys automáticos rápidos e limpos:

1. **PROIBIDO Git Submodule:**
   O uso de submódulo git para o `suape-brand` é expressamente proibido. Submódulos exigem tokens adicionais no Cloud Build e geram frequentes falhas de checkout em esteiras de CI/CD.
2. **PROIBIDO commitar o kit inteiro:**
   O repositório do kit contém pacotes, fontes completas e scripts de build. Commitar o kit inteiro duplica dezenas de arquivos desnecessários na sua base de código.
3. **Copie apenas os assets necessários:**
   Copie os arquivos SVG (`logo-horizontal.svg`, `isotipo.svg`), as fontes e os componentes de splash que seu frontend for usar diretamente para a pasta estática do projeto (ex.: `web/public/brand/` ou `web/src/components/brand/`).
4. **Adicione ao `.gitignore` se clonar para consulta:**
   Caso você clone o repositório `suape-brand` na raiz do seu projeto para extrair arquivos ou testar componentes, adicione a pasta ao seu `.gitignore`:
   ```gitignore
   # Kit da marca clonado para consulta local
   suape-brand/
   ```

---

## Checklist de Identidade Visual

Antes de solicitar provisionamento do ambiente no GCP, confira:

- [ ] Splash screen oficial integrada e exibindo a animação homologada no carregamento inicial.
- [ ] A splash screen está configurada para exibir apenas **uma vez por sessão** de navegação.
- [ ] Logotipos horizontais e quadrados importados diretamente dos SVGs oficiais do kit.
- [ ] Logotipo preserva a área de respiro mínima (altura do sol central) sem invasão de outros elementos.
- [ ] Nenhuma distorção de proporção (aspect ratio) aplicada à marca.
- [ ] Logotipo monocromático branco utilizado em fundos escuros ou no azul institucional.
- [ ] Paleta institucional aplicada (`#3257A4` e `#FAB400`), sem textos claros sobre fundo amarelo.
- [ ] Tipografia institucional Matt aplicada nos pesos homologados (400 e 700).
- [ ] O repositório não possui Git Submodule e a pasta `suape-brand/` está no `.gitignore` caso tenha sido clonada localmente.
