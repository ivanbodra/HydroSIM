# Tratado pedagógico do PED-D1 — Fundamentos acústicos pela observação conectada

Revisão: 1.0 — 16 de outubro de 2026.
Edição em português correspondente à [revisão canônica 1.0 em inglês](../PED-D1_acoustic_foundations.md).
Esta edição acompanha as mesmas seções e preserva as decisões, recomendações e limites; algumas tabelas são apresentadas de forma condensada.
Responsável: caho-pedagogy. Autoridade final: Product Owner.
Destino: próxima geração do HydroSIM.
Implementação examinada: eed7bedc19f654b9adc13275a249a57576720e5d.
Situação: direção pedagógica registrada; tratamento recomendado; extensão científica e conceito visual pendentes.

## 1. Mandato e origem das decisões

A discussão com o Product Owner, em 16/10/2026, estabelece as seguintes direções:

1. O D1 introduz a experiência dos laboratórios e deve construir uma intuição que cresça ao longo da sequência.
2. A estrutura existente é aproveitável, mas os labs precisam ganhar profundidade, precisão e substância pedagógica.
3. A frequência permanece como principal controle físico; os demais controles são secundários.
4. A experiência deve incorporar representações físicas e observações conectadas, ampliando o uso das senoides.
5. O D1 deve consolidar o significado de onda sonora, pressão, potência, referência logarítmica e observação no espaço e no tempo.
6. Os labs devem manter harmonia e um padrão reconhecível de controle e visualização.
7. Os tratados pedagógicos orientarão uma nova versão do HydroSIM.

Essas são direções do Product Owner. A sequência de atividades, a organização das cenas e os critérios abaixo são recomendações pedagógicas construídas a partir delas.

As equações que relacionam pressão, movimento das partículas, intensidade e potência pertencem ao Scientific Lead. A ampliação do objetivo pedagógico não autoriza trocar o rótulo da amplitude normalizada atual por Pa, watts ou níveis calibrados.

## 2. O papel do D1 na aprendizagem cumulativa

O D1 deve formar uma imagem explicativa do fenômeno e uma maneira de explorar os labs seguintes.

Ao concluí-lo, o aluno deve conseguir distinguir o que oscila localmente, o que se propaga, o que pode ser medido e como uma observação se transforma em gráfico. Deve reconhecer frequência, período, comprimento de onda, amplitude e fase nessas observações.

Pressão, intensidade, potência e níveis relativos ampliam essa compreensão. A profundidade surge de novas perspectivas sobre um mesmo fenômeno, com complexidade progressiva.

A abertura precisa fazer sentido sem experiência prévia em um sistema de aquisição. A conclusão deve preparar o vocabulário que reaparecerá em pulsos, orçamento acústico, arrays e medições.

O D1 não precisa concentrar simultaneamente todos os gráficos, controles e definições. Também não deve absorver a matéria inteira dos labs seguintes.

## 3. Avaliação da versão atual

Fontes examinadas: especificação pedagógica e visual do D1, contrato científico PED-D1/PED-D2 e WaveLab.tsx da implementação indicada.

Convém preservar:
- frequência em destaque;
- controles secundários com revelação progressiva;
- redefinição do experimento;
- cálculo fornecido pelo Core/API;
- período e comprimento de onda como resultados;
- escalas de amplitude estáveis e comparação com referência.

Os principais limites identificados no código são:

| Condição atual | Problema pedagógico | Direção recomendada |
|---|---|---|
| Duas senoides concentram a experiência | O significado físico do gráfico permanece pouco explícito | Cena longitudinal ligada à observação selecionada |
| O instante solicitado para o perfil espacial permanece em zero | Falta explorar a evolução temporal de forma deliberada | Reproduzir, pausar e avançar sob uma mesma referência temporal |
| Os gráficos de tempo e espaço têm pouca correspondência explícita com o meio | O aluno precisa descobrir sozinho o que está fixo em cada vista | Ponto de observação e instante selecionado ligados aos gráficos |
| Faixa de 20–700 kHz, janela temporal de 14 microssegundos e espacial de 22,4 mm | Nas menores frequências não cabe um ciclo completo e os marcadores desaparecem | Faixas e escalas coerentes com a medição de ciclos |
| Não há tarefa de previsão e explicação | Mover o controle não demonstra compreensão | Explorações curtas que exijam interpretação |
| A amplitude é normalizada | Não sustenta uma leitura quantitativa de pressão ou potência | Extensão científica explícita |
| A referência é inicializada pelo primeiro resultado recebido, mas tem legenda fixa | O rótulo não garante a identidade do estado comparado | Referência definida por configuração explícita |

Em 20 kHz, o período é 50 microssegundos. Com velocidade de 1500 m/s, o comprimento de onda é 75 mm. Esses valores ilustram a incompatibilidade com as janelas atuais.

São achados de inspeção da implementação, sem certificação de usabilidade em execução ou estudo de aprendizagem com alunos.

## 4. Conexão com o CAHO

A referência curricular examinada é Acústica Submarina, 1 - Aula Inicial_3h.pdf, identificada como CAHO-AC-01:

- página PDF 5: objetivos de propagação e aplicação em instrumentos;
- páginas PDF 29–30: onda de pressão, compressões e rarefações;
- páginas PDF 33–38: oscilação, amplitude, período, frequência e fase;
- páginas PDF 49–52: interferência e diferença de fase;
- página PDF 13: estrutura das unidades da disciplina.

A numeração acima é a posição da página no PDF; os números impressos dos slides apresentam diferenças.

O texto da apresentação foi lido, com inspeção visual amostral das páginas 5, 13, 29 e 48. A identidade da fonte e a extensão da leitura constam do [registro inicial do CAHO](https://github.com/ivanbodra/HydroSIM/blob/7beeac3de7afe3753b533587475cb524fe99c141/docs/pedagogy/caho/reading_log.md), proposto no PR #606.

A sequência completa pressão–potência–decibéis deste tratado é uma ampliação do HydroSIM orientada pelo Product Owner. Não é apresentada como transcrição de um objetivo da disciplina ou análise integral de uma unidade ainda não lida.

## 5. Público, pré-requisitos e objetivos de aprendizagem

Público: oficiais-alunos do CAHO iniciando a sequência acústica e pessoas revisando seus fundamentos.

A abertura exige apenas noções básicas de tempo, distância, unidades e variação de uma grandeza. A compreensão inicial não deve depender de exponenciais complexas ou experiência com o sonar.

O aluno deverá demonstrar que consegue:

| Objetivo | Evidência observável |
|---|---|
| O1 — Distinguir oscilação local e propagação | Acompanhar uma partícula e uma compressão e explicar seus movimentos |
| O2 — Identificar a grandeza observada | Distinguir deslocamento, pressão acústica e representação normalizada |
| O3 — Separar tempo e espaço | Explicar o que está fixo no registro temporal e no perfil espacial |
| O4 — Relacionar frequência, período e comprimento de onda | Prever uma alteração antes de manipular a frequência |
| O5 — Separar frequência e velocidade de propagação | Explicar o efeito de mudar a velocidade mantendo a frequência |
| O6 — Distinguir amplitude e fase | Identificar suas consequências sem atribuir mudança de frequência |
| O7 — Distinguir pressão, intensidade e potência | Nomear grandezas, unidades, contexto e condições para relacioná-las |
| O8 — Interpretar nível logarítmico | Identificar a referência e separar mudança de representação de mudança física |
| O9 — Comparar casos controlados | Preservar a referência e isolar uma variável |
| O10 — Transferir a intuição | Reconhecer o vocabulário que será usado em pulsos e orçamento acústico |

O7 e O8 dependem dos novos resultados científicos. A existência do D1 normalizado atual não demonstra que esse novo objetivo esteja cumprido.

## 6. Fenômeno central e pergunta organizadora

A experiência deve conectar:

movimento do meio e variação de pressão -> propagação -> observação em um ponto fixo -> retrato espacial -> relações derivadas -> grandezas físicas -> níveis relativos.

Pergunta central:

**O que muda na água, o que um observador mede e como nossas escolhas alteram o fenômeno e sua representação?**

O meio de referência começa homogêneo. Cada nova camada de complexidade deve permitir descobrir uma relação adicional.

## 7. Três perspectivas que precisam permanecer distintas

A cena deve permitir selecionar:

1. Uma partícula material, associada à sua posição de equilíbrio e ao seu deslocamento local.
2. Um ponto fixo no espaço, associado ao registro de pressão naquele local.
3. Um instante, associado à distribuição de pressão ao longo do espaço.

A partícula marcada e o ponto de medição não devem se transformar silenciosamente no mesmo objeto.

Um gráfico de deslocamento e um gráfico de pressão precisam identificar grandezas, unidades e relações de fase próprias. A senoide de pressão não representa uma trajetória transversal da partícula.

Compressões e rarefações devem ser perceptíveis. Se o deslocamento ou o contraste visual estiverem ampliados, isso precisa ser informado. Os pontos desenhados representam elementos do meio; não devem sugerir uma simulação molecular literal.

Uma região de compressão pode marcar a propagação, enquanto a partícula marcada permite observar a oscilação local. A coerência entre esses campos será definida cientificamente; sua composição será desenvolvida pelo Concept Designer.

## 8. Percurso progressivo da experiência

| Etapa | Pergunta | Interação | Descoberta |
|---|---|---|---|
| A — Observar o meio | O que oscila e o que viaja? | Reproduzir, pausar, avançar e selecionar marcas | Oscilação local e propagação são diferentes |
| B — Observar um local | O que um observador estacionário registra? | Selecionar a sonda e acompanhar o tempo | Frequência e período caracterizam o registro temporal |
| C — Congelar um instante | Como a grandeza está distribuída agora? | Pausar e medir estados equivalentes no espaço | Comprimento de onda é uma distância |
| D — Controlar frequência e velocidade | O que cada alteração modifica? | Frequência primeiro; velocidade depois | Separar rapidez da oscilação, avanço da onda e distância entre repetições |
| E — Separar magnitude e fase | O que muda sem mudar a frequência? | Controles secundários de amplitude e fase | Distinguir magnitude, fase e taxa de oscilação |
| F — Examinar as grandezas | Como pressão se relaciona ao transporte de energia? | Inspecionar campos e relações validadas | Diferenciar pressão, intensidade e potência |
| G — Mudar a representação | O que significa um nível relativo? | Comparar valores lineares e logarítmicos | Distinguir estado físico, escala e referência |

A proposta é um lab com profundidade progressiva. As perspectivas compartilham o caso configurado, a referência e as seleções; não são sete aplicações desconectadas.

Devem existir exploração guiada e exploração livre. Perguntas não precisam bloquear o acesso aos controles.

O instrutor pode usar A–D em um momento da disciplina e retornar a F–G depois. O objetivo completo da nova versão inclui F–G; a necessidade de nova ciência não justifica descartá-las.

## 9. Hierarquia de controles e significado dos estados

A frequência permanece visível e dominante.

Amplitude, fase e velocidade do som são controles físicos secundários. Amplitude física e amplitude normalizada precisam ser identificadas de modo inequívoco; o aluno deve saber qual delas está usando.

Reproduzir, pausar, avançar e câmera lenta controlam a inspeção do tempo. Não devem parecer controles da velocidade física do som.

A seleção de partícula, ponto de observação e instante deve ocorrer diretamente na cena sempre que útil. Unidades, vista linear/logarítmica e sobreposição de referência são controles de representação.

Salvar referência, restaurá-la e redefinir o experimento precisam ter comportamento previsível e reaproveitável nos outros labs.

Período e comprimento de onda continuam derivados. Alterar apenas a referência de apresentação ou trocar uma vista não deve reconfigurar silenciosamente o fenômeno.

O contrato atual classifica o campo analítico como Configured/Derived. Uma sonda simulada não é uma observação ambiental real nem uma medição de hardware calibrado.

Ao mudar uma propriedade física, é necessário declarar as demais condições mantidas. Na extensão pressão–intensidade, mudar a velocidade do som pode alterar outros resultados conforme o modelo; não se deve prometer invariância energética sem definir as restrições.

## 10. Outputs exigidos e seu significado

| Output | O que precisa comunicar |
|---|---|
| Cena longitudinal | Equilíbrio, deslocamento local, compressões/rarefações e direção de propagação |
| Registro temporal | Grandeza em uma posição estacionária; cursor ligado ao instante da cena |
| Perfil espacial | Grandeza em um instante; posição da sonda identificada |
| Marcadores de T e comprimento de onda | Repetição completa medida no eixo correto |
| Resumo f, c, T e comprimento de onda | Relações derivadas com unidades legíveis |
| Pressão | Valor instantâneo, pico/RMS conforme convenção; distinção da pressão estática |
| Intensidade e potência | Grandezas distintas, com meio, direção, superfície e média necessários |
| Vista linear/logarítmica | Grandeza, estatística, referência e caso físico identificados |
| Comparação | Referência e estado atual com identidade explícita e escalas compatíveis |
| Registro da exploração | Previsão, observação e explicação do aluno |

Para exemplos ultrassônicos, microssegundos e milímetros frequentemente facilitam a leitura. O eixo deve identificar a grandeza e a unidade.

Valores configurados, valores de uma sonda simulada, resultados derivados e referências não devem ser chamados indiscriminadamente de medições.

## 11. Escalas, referência e animação

A faixa de controles deve permitir observar e medir ciclos completos. Para as comparações de ciclos, o aluno deve ter acesso a pelo menos duas repetições, inclusive nas menores frequências suportadas, e também a uma inspeção detalhada.

Uma possibilidade é combinar visão geral e ampliação explícita, compartilhada entre referência e estado atual. A solução visual final pertence ao Designer.

Não se deve normalizar silenciosamente cada onda para ocupar sempre o mesmo número de ciclos. Também não se deve alterar separadamente os eixos de duas curvas comparadas.

A referência deve nascer de uma configuração declarada, com seus valores reais. Ela não pode depender da ordem de chegada das respostas da API.

As vistas simultâneas precisam compartilhar tempo e contexto de observação. A câmera lenta altera a reprodução, não a velocidade física. Aumentar a frequência com velocidade fixa não pode acelerar indevidamente a marca de propagação.

Redefinir e restaurar referência devem ter efeitos claros sobre tempo e seleções. Oferecer pausa, avanço e imagens estáticas significativas também é necessário para acessibilidade.

## 12. Pressão, intensidade, potência e referência logarítmica

O objetivo pedagógico é distinguir as grandezas e compreender as condições que permitem relacioná-las.

O modo quantitativo de pressão precisa definir a perturbação acústica em relação à pressão estática, a estatística de entrada, a unidade e sua relação com o movimento das partículas. A pressão em uma sonda não deve ser apresentada automaticamente como potência total emitida pela fonte.

Uma demonstração de potência precisa de superfície, geometria, direção e média explicitadas. Se for adotado um exemplo de fluxo através de uma superfície, o rótulo deve comunicar esse significado. Área e propriedades do meio podem inicialmente permanecer fixas e declaradas.

Para a parte logarítmica, o aluno deve reconhecer a grandeza, a referência linear e a convenção do nível. Um experimento especialmente útil mantém o caso físico e altera apenas a referência usada para reportar o nível.

Nível positivo ou negativo não representa o sinal instantâneo da pressão nem distingue compressão de rarefação. A pressão instantânea e o nível estatístico precisam de representações apropriadas.

Amplitude nula e situações em que o logaritmo não está definido exigem comportamento explícito. Não se deve fabricar um valor finito ou esconder o problema num limite gráfico.

Equações, referências numéricas, exemplos de razões, relações de fase e testes pertencem à extensão científica. O tratado estabelece a consequência pedagógica desejada.

## 13. Experimentos guiados

A sequência recorrente será: prever -> manipular -> observar -> comparar -> explicar -> aplicar.

| Experimento | Comparação | Evidência solicitada |
|---|---|---|
| E1 — Movimento local e propagação | Partícula marcada e compressão ao longo do tempo | Explicar qual se desloca através da cena e qual retorna ao equilíbrio |
| E2 — Ponto fixo e retrato espacial | Mesmo campo, local e instante ligados às vistas | Identificar o que está fixo em cada gráfico |
| E3 — Frequência | Mudar f mantendo c e a convenção de amplitude | Prever T e comprimento de onda; identificar invariantes |
| E4 — Velocidade do som | Mudar c mantendo f | Separar período temporal de avanço e periodicidade espacial |
| E5 — Amplitude | Mudar a amplitude declarada com f e c fixos | Distinguir magnitude de frequência e interpretar as relações autorizadas |
| E6 — Fase | Mudar fase inicial mantendo o restante | Explicar o deslocamento sem inventar frequência ou atraso de propagação |
| E7 — Grandezas físicas | Examinar o mesmo caso físico validado | Nomear grandezas, unidades e condições |
| E8 — Linear e nível relativo | Preservar o fenômeno e alterar representação/referência | Explicar a mudança numérica e a permanência física |
| E9 — Transferência | Interpretar uma afirmação acústica hidrográfica simples | Dizer o que está definido e quais informações ainda seriam necessárias |

As perguntas devem ser curtas e contextuais. Uma explicação longa não substitui a relação observável.

## 14. Concepções equivocadas a tornar observáveis

| Risco | Resposta da experiência |
|---|---|
| A água viaja com a onda | Equilíbrio e partícula local distintos da marca de propagação |
| A senoide é a trajetória da partícula | Grandeza identificada e ligação à cena longitudinal |
| Partícula e ponto fixo são o mesmo observador | Objetos e seleções distintos |
| Pressão e deslocamento têm unidade/fase iguais | Campos separados e relação validada |
| Frequência maior acelera a propagação neste modelo | Experimento com c fixo |
| Alterar f apenas aplica zoom | Escalas explícitas e referência consistente |
| Pressão, intensidade e potência são intercambiáveis | Grandezas, unidades e condições próprias |
| Fase inicial significa atraso de propagação | Experimento com invariantes explícitos |
| Pressão acústica é a pressão estática | Perturbação e fundo estático diferenciados |
| dB dispensa grandeza ou referência | Definição e referência visíveis |
| 0 dB é ausência de som ou dB negativo é rarefação | Separação entre nível relativo e sinal físico |
| Uma animação convincente comprova a física | Resultados canônicos, casos-limite e validação independente |

Esses são riscos pedagógicos previstos, não uma estatística de dificuldades dos alunos do CAHO.

## 15. Evidências de aprendizagem

A avaliação será formativa:

- previsão antes de uma alteração principal;
- medição de um ciclo no tempo e no espaço;
- explicação das diferenças entre partícula, sonda fixa e instante;
- comparação controlada com identificação do que permaneceu fixo;
- classificação de pressão, intensidade e potência, com unidades e uma condição;
- explicação de uma mudança de escala ou referência;
- aplicação do vocabulário em uma situação que prepara os labs seguintes.

Uma previsão inicialmente errada pode resultar em aprendizagem bem-sucedida se o aluno a confrontar com a evidência e revisar a explicação.

Acertar posições de sliders não basta. Não é necessário criar porcentagens de qualidade ou certificar competência operacional a partir do D1.

## 16. Gramática visual comum, acessibilidade e linguagem

O padrão a amadurecer para os outros tratados é:

**controle -> mudança física -> medição observável -> comparação -> explicação ou decisão.**

Devem permanecer reconhecíveis o controle principal, o estado físico, a referência, o estado atual, a observação selecionada e a consequência derivada.

Cena, gráfico e leitura devem responder à mesma seleção. A mudança relevante pode receber ênfase local e breve; não é necessário fazer toda a tela piscar. A cena física tem maior hierarquia que cartões auxiliares de métricas.

O Concept Designer definirá a expressão visual. Não se estabelece aqui uma paleta ou um layout obrigatório para todos os fenômenos.

Exigir operação por teclado, rótulos e contraste legíveis, informação além das cores, pausa/avanço, redução de movimento e descrições acessíveis concisas. EN/PT-BR devem preservar grandezas e hipóteses. Não apresentar uma sonificação como reprodução direta de frequências ultrassônicas.

## 17. Continuidade com os próximos labs

| Lab posterior | Base fornecida pelo D1 | Assunto que permanece no outro lab |
|---|---|---|
| PED-D2 | Portadora, registro temporal, amplitude, fase e unidades | Pulso finito, banda, CW/chirp, envoltória e filtro casado |
| PED-D3 | Grandezas físicas, referências e interpretação de níveis | Fonte/recepção, perdas, ruído, SNR e orçamento acústico |
| PED-D4 | Velocidade em meio homogêneo e geometria da observação | Perfis, refração e erro de reconstrução |
| PED-D6/PED-D7 | Comprimento de onda, fase e observação coerente | Arrays, canais, interferência e steering |
| Demais labs | Comparação controlada e disciplina de grandezas | Seus fenômenos e decisões operacionais |

Não ampliar o D1 para resolução batimétrica, orçamento sonar completo, eficiência real de transdutores, oceano complexo ou detecção do fundo apenas para aumentar sua aparência de complexidade.

## 18. Dependências científicas e de implementação

A cinemática existente é reaproveitável onde satisfizer o objetivo. Seu contrato normalizado não autoriza por si só pressão, movimento de partículas, intensidade ou potência.

Perguntas executáveis ao Scientific Lead:

- SQ1: quais campos consistentes representarão pressão, deslocamento/velocidade das partículas e compressão, com unidades, sinais, fase e limites?
- SQ2: qual convenção de pressão será usada e como ela se relaciona, ou permanece separada, da amplitude normalizada?
- SQ3: qual demonstração mínima de intensidade/potência será adotada, com meio, direção e superfície/geometria declarados?
- SQ4: quais níveis, referências, estatísticas e comportamentos em zero/indefinição serão suportados?
- SQ5: quais condições permanecem fixas quando um controle muda, como compartilhar o tempo observado e quais casos independentes validarão os resultados?

O Core/API fornece a ciência. A interface pode projetar e animar o estado, mas não criar um segundo modelo acústico.

O Designer desenvolve a cena e a gramática de observação, identificando as saídas ainda pendentes. Software Engineering avalia modelo/API/runtime após as decisões científicas; UX implementa; QA verifica o candidato exato.

As pendências bloqueiam apenas a implementação das saídas afetadas, não a publicação do tratado nem a exploração visual da cinemática já definida.

## 19. Critérios de aceitação pedagógica da nova versão

1. Cena física, sonda fixa, retrato espacial e gráficos descrevem um fenômeno coerente.
2. Partícula, sonda e marca de propagação são distinguíveis.
3. Cada campo identifica grandeza, unidade e contexto.
4. Frequência é o controle principal, com os demais progressivamente disponíveis.
5. Frequência e velocidade produzem consequências distintas e corretas.
6. Reprodução, pausa, avanço e câmera lenta preservam as relações físicas.
7. É possível observar e medir ciclos completos na faixa suportada.
8. Referência e estado atual têm identidade e escalas apropriadas explícitas.
9. Pressão física não é inventada por uma troca de rótulo.
10. Pressão, intensidade e potência têm diferenças e condições claras.
11. Níveis identificam estatística e referência, incluindo casos indefinidos.
12. Mudanças apenas de representação preservam o estado físico.
13. As tarefas produzem previsão, comparação, explicação e transferência.
14. Acessibilidade e EN/PT-BR preservam os mesmos conceitos.
15. D2 e D3 reutilizam o vocabulário estabelecido.
16. Ciência, conceito visual e runtime são verificados no candidato exato.
17. A revisão com instrutor/alunos verifica se as explicações pretendidas são alcançadas.
18. O Product Owner aceita a experiência resultante.

A prontidão histórica da versão normalizada não encerra esses novos requisitos.

## 20. Sequência de desenvolvimento

1. Registrar tratado, edição em português e ligação na especificação modular.
2. Scientific Lead resolver SQ1–SQ5 em contrato/extensão com referências e validação.
3. Concept Designer propor a experiência conectada, coordenada com as saídas científicas.
4. Technical Lead sequenciar a implementação e suas parcelas entregáveis.
5. Core/API e UX implementar o tratamento aprovado.
6. QA verificar consistência de grandezas, fase, tempo, escalas, referência e consequências pedagógicas.
7. Integrar, realizar revisão focada com instrutor/alunos e obter aceitação do Product Owner.
8. Repetir o processo para D2 e os próximos labs, sem presumir seus tratados antes da revisão conjunta.

O tratado não atribui automaticamente número de versão nem publica ou implanta software.

## 21. Fontes e função de cada uma

- Discussão com o Product Owner em 16/10/2026: direção pedagógica e intenção de nova versão.
- CAHO-AC-01: vínculo curricular, com páginas e extensão da leitura indicadas na seção 4.
- Especificações e código atuais do D1: base reaproveitável e limitações identificadas.
- [DOSITS / University of Rhode Island — What is sound?](https://dosits.org/science/sound/what-is-sound/): referência pedagógica para relacionar meio, movimento e propagação.
- [DOSITS — What is intensity?](https://dosits.org/science/advanced-topics/what-is-intensity/): referência para distinguir fluxo de energia e grandezas.
- [DOSITS — Introduction to Decibels](https://dosits.org/science/advanced-topics/introduction-to-decibels/): referência para o tratamento de grandezas lineares e níveis relativos; sua exposição simplificada não substitui o contrato científico.
- [NPL — Good practice guide for underwater noise measurement, GPG133, 2014](https://eprintspublications.npl.co.uk/6121/): referência técnica candidata ao Scientific Lead. Metadados localizados; texto completo não recuperado neste ciclo.

As referências sustentam a proposta pedagógica. As equações, hipóteses e fontes de validação da extensão implementada deverão ser documentadas pelo responsável científico.

## 22. Histórico da revisão

Revisão 1.0, 16/10/2026: tratado inicial após revisão conjunta do D1; ampliação para fenômeno, observação e grandezas físicas; frequência preservada como controle principal; progressão, coerência entre labs, dependências e critérios de aceitação registrados.
