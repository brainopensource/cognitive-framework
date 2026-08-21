# Substratos Agênticos Compostos: da Teoria da Composabilidade à Arquitetura do Vanguard/AETHER

### Resumo para leitura em aula

---

## Capítulo 1 — A Pesquisa: o que significa construir um substrato, e não um agente

### 1.1 O problema de fundo

A pergunta central de toda esta linha de investigação não é "como construir um bom agente de código", mas "como construir a coisa a partir da qual muitas gerações de agentes podem ser construídas". Essa distinção parece sutil, mas ela determina decisões arquiteturais irreversíveis. Um framework desenhado para um agente tende a cristalizar decisões específicas de domínio — como o modelo pensa, como ele planeja, como ele é avaliado — dentro do próprio núcleo do sistema. Um substrato, por definição, recusa-se a fazer isso: ele oferece primitivas gerais o suficiente para que "agente de código", "agente de pesquisa", "sistema de debate entre modelos" ou "busca em árvore guiada por modelo" sejam todas apenas composições diferentes sobre a mesma máquina.

A tese que guia esta investigação é que a maioria dos frameworks de agentes falha não por falta de poder expressivo, mas por excesso de acoplamento entre a parte que decide, a parte que executa e a parte que julga. Quando essas três responsabilidades se misturam, o sistema perde a capacidade de gerar evidência confiável sobre si mesmo — e sem evidência confiável, nenhuma forma futura de auto-aperfeiçoamento ou meta-cognição é sequer definível.

### 1.2 A tese da separabilidade

Existe uma ideia organizadora que atravessa toda a literatura séria sobre avaliação de sistemas autônomos: **aquilo que resolveu o problema precisa ser separável daquilo que julgou a solução, e o juiz precisa ser inalcançável por aquele que está sendo julgado.**

Isto não é uma preocupação de segurança acessória — é uma condição de possibilidade. Um agente que passa em um benchmark não constitui evidência de competência se o mecanismo que produziu a resposta tiver qualquer forma de acesso, influência ou visibilidade sobre o mecanismo que gerou a nota. Isso vale tanto para trapaça deliberada quanto para vazamento estatístico sutil. Um sistema que respeita essa separação de forma estrutural — e não apenas por convenção de engenharia — ganha algo raro: um sinal de treinamento que não pode ser corrompido pelo próprio agente que o produziu.

### 1.3 Três planos de responsabilidade

Uma arquitetura agêntica madura tende a se organizar, mesmo que implicitamente, em três planos distintos:

O **plano de decisão** é responsável por escolher quem age, quando age, com que orçamento e com que autorização. É volátil por natureza — pode ser reconstruído, recalculado, refeito.

O **plano de estado** é a única fonte de verdade sobre o que de fato aconteceu. Ele não pode ser a memória de um orquestrador em processo, porque memória em processo desaparece com uma queda de energia e, pior, pode ser reescrita silenciosamente. Estado confiável precisa ser derivado de um registro imutável de eventos — o sistema "lembra" recalculando a partir da história, nunca guardando um resumo que ninguém pode auditar.

O **plano de evidência** é onde o julgamento acontece, e ele precisa viver fora do alcance dos outros dois. Um agente nunca deveria ser capaz de ler, influenciar ou dialogar com o mecanismo que o avalia.

Frameworks que colapsam esses três planos em um único objeto de execução parecem mais simples no curto prazo, mas perdem justamente a propriedade que permite, mais tarde, fazer ciência sobre o próprio sistema.

### 1.4 Identidade experimental: por que um único identificador não basta

Um erro comum e caro é usar um único identificador — um "hash da composição" — para responder simultaneamente a três perguntas diferentes: qual é a composição do agente, qual foi a execução específica, e qual foi o experimento comparativo do qual essa execução faz parte. Essas três noções de identidade precisam ser mantidas separadas. Se a identidade da composição não capturar tudo que afeta o comportamento — incluindo o texto do prompt, o teto de capacidades e as rotas de modelo — dois agentes com comportamentos radicalmente diferentes podem, incorretamente, compartilhar a mesma identidade, e toda comparação estatística feita sobre esse dado se torna inválida.

Isso é o que se poderia chamar de **os denominadores da medição**: antes de existir qualquer capacidade de comparar A contra B, é preciso que essas três noções de identidade estejam bem definidas e nunca colapsadas entre si.

### 1.5 Recursão como primitiva única

A tentação natural, ao projetar um sistema que precisa suportar agentes, sub-agentes, delegação hierárquica e eventualmente enxames de agentes cooperando, é criar um tipo especial para cada caso: um tipo para agente, outro para sub-agente, outro para agente coordenador, outro para participante de enxame. Essa tentação deve ser resistida. A alternativa mais robusta — e mais difícil de conceber corretamente da primeira vez — é ter **uma única primitiva de delegação**, com uma única regra de atenuação: um agente delegado nunca pode ter mais capacidade ou mais orçamento do que quem o delegou. Coordenação de múltiplos agentes, nessa visão, deixa de ser um motor novo dentro do sistema e passa a ser apenas uma **política** aplicada sobre agentes que já existem. Relações causais entre agentes — quem gerou quem, quem foi avaliado por quem — tornam-se **projeções sobre o histórico de eventos**, nunca uma estrutura de grafo que o sistema precisa manter e sincronizar como verdade paralela.

### 1.6 O que deve ser mecanismo e o que deve ser plugin

Toda arquitetura composável enfrenta a mesma decisão fundamental, repetidamente: este comportamento deve viver *abaixo* da linha de extensão — como parte confiável e imutável do núcleo — ou *acima* dela, como uma estratégia substituível?

A resposta que a pesquisa contemporânea sugere, e que esta investigação corrobora, é que a linha correta não separa "coisas simples" de "coisas complexas", mas sim **autoridade** de **estratégia**. Tudo que envolve mediar efeitos, conceder ou negar capacidades, escrever no registro de eventos, ou assinar um veredito, precisa permanecer mecanismo — pequeno, auditável, e o mesmo para todo composição possível. Tudo que envolve *como pensar*, *como planejar*, *como lembrar*, *como montar contexto*, *como escolher entre modelos* — isso é estratégia, e deve ser plugin.

### 1.7 O contraponto radical: arquiteturas onde "tudo é plugin"

Existe atualmente, no cenário de harnesses agênticos, uma corrente que leva a composabilidade ao extremo: absolutamente tudo — o modelo, as ferramentas, a sessão, o sandbox, o armazenamento, o próprio laço de execução do agente e até a interface — é implementado como plugin substituível, montado e desmontado dinamicamente por um núcleo que deliberadamente **não reivindica nenhum privilégio central**. A promessa dessa abordagem é uma liberdade de composição quase total: qualquer parte do sistema pode ser trocada sem tocar em código-fonte, e um registro de sessão em formato de log de eventos permite reconstruir, bifurcar e repetir qualquer execução.

Essa abordagem tem uma virtude genuína, que vale a pena importar: a **superfície de composição totalmente plana**. Não existir uma distinção rígida de "slots" fixos onde cada tipo de componente deve caber é o que permite expressar rapidamente formas de agente muito diferentes entre si.

Mas essa abordagem também tem um custo que precisa ser nomeado com clareza: ao recusar qualquer núcleo privilegiado, ela recusa também a possibilidade de um **plano de autoridade real** — não há reforço estrutural de que um plugin não pode forjar um veredito, ampliar seu próprio orçamento, ou escrever diretamente uma "verdade" no histórico que não corresponde ao que de fato ocorreu. Composabilidade extrema e ausência de autoridade tendem a andar juntas na prática, mas **não são a mesma coisa**, e nada impede, em princípio, que um sistema tenha as duas propriedades — uma superfície de composição totalmente flexível, construída sobre um núcleo pequeno e não-negociável que continua mediando toda concessão de capacidade e todo registro de evidência.

### 1.8 Determinismo, repetição e o que "lembrar" realmente significa

Uma propriedade frequentemente reivindicada e raramente comprovada é a de que o sistema pode "repetir" uma execução passada. É essencial distinguir níveis diferentes dessa afirmação. Reconstruir o estado — quem tinha que capacidade, quanto orçamento restava, quais aprovações existiam — a partir do histórico bruto, em um processo novo, é uma prova forte. Dobrar duas vezes a mesma lista de eventos já carregada em memória não prova nada além de que a função de dobra é determinística, o que ninguém duvidava. Essa distinção parece pedante até o momento em que alguém precisa confiar na reprodutibilidade do sistema para investigar um incidente ou para gerar dados de treinamento — e descobre que a "prova de repetição" que existia nunca testou o caminho que importa.

### 1.9 O que a evidência precisa carregar para permitir aprendizado futuro

A última peça teórica é talvez a mais frequentemente negligenciada: gerar um registro de execução que seja *validável contra um esquema* não é o mesmo que gerar um registro que seja *útil para aprender algo*. É perfeitamente possível produzir uma trajetória de execução tecnicamente correta e completamente vazia de conteúdo — sem custo real por turno, sem a identidade do modelo usado, sem o veredito embutido. Qualquer trabalho futuro de otimização, seja ele calibração de política, seleção de estratégia ou destilação de modelo, depende inteiramente da riqueza desse dado bruto. A disciplina correta é: o sistema primeiro precisa produzir dados confiáveis sobre suas próprias execuções; só depois, e apenas depois, faz sentido construir qualquer mecanismo de otimização que consuma esses dados.

---

## Capítulo 2 — A Aplicação: o Vanguard/AETHER à luz dessa teoria

### 2.1 O veredito, apresentado primeiro

Avaliando o projeto Vanguard/AETHER contra todo o corpo teórico do primeiro capítulo, a conclusão é clara e pode ser enunciada em uma frase: **o projeto está de fato construindo um substrato geral, não apenas um harness de codificação com um núcleo de segurança anexado.** As decisões mais difíceis e mais irreversíveis — autoridade como mediador central de efeitos, estado como reconstrução a partir de eventos, avaliação por um juiz exterior e inalcançável, identidade dividida em três dimensões distintas, delegação como primitiva única — foram todas tomadas na sua forma geral, e não na forma específica de um agente de codificação, e foram tomadas antes de existir qualquer pressão de produto exigindo isso. Essa é precisamente a assinatura de um projeto que está construindo infraestrutura durável, e não um produto disfarçado de infraestrutura.

Dito isso, a superfície pela qual um desenvolvedor efetivamente compõe um novo agente ainda está moldada como o primeiro caso de uso — a codificação —, e é essa superfície, não os fundamentos, que precisa evoluir antes que a ambição do projeto se torne plenamente alcançável.

### 2.2 O que já está estruturalmente forte

O núcleo de despacho de efeitos do sistema já funciona como um verdadeiro monitor de referência: toda concessão de capacidade é vinculada a um descritor específico, toda atenuação de capacidade para um agente delegado é verificada, e a intenção de executar um efeito é tornada durável antes mesmo do efeito ocorrer — o que fecha uma classe inteira de bugs onde o sistema "esquece" que estava no meio de uma operação perigosa.

A separação entre os três planos discutidos no capítulo anterior não é apenas uma aspiração de documento — ela está de fato implementada: existe um único algoritmo de canonicalização de bytes usado para toda assinatura e todo hash; existe uma única álgebra de seletores de recursos usada como a única relação de inclusão do sistema inteiro; e existe um registro de eventos com verificação a frio — ou seja, reconstruído de fato a partir do disco, em um processo novo, e comparado byte a byte com o estado ao vivo. Essa é exatamente a versão forte do determinismo discutida na seção 1.8, não a versão fraca.

O juiz permanece uma identidade de processo separada, com assinatura criptográfica vinculada ao pedido específico de avaliação, tornando impossível — não apenas improvável — que um veredito falso seja aceito sem assinatura válida.

A primitiva de delegação segue exatamente a receita da seção 1.5: agente e sub-agente são o mesmo tipo de objeto, a diferença é apenas a presença de uma referência ao pai; coordenação entre múltiplos agentes é tratada explicitamente como política, nunca como um motor separado; e a álgebra de orçamento distingue corretamente entre recursos que se conservam de forma aditiva — como custo em dinheiro ou tokens — e restrições estruturais, como profundidade de recursão, que não devem ser somadas entre agentes irmãos. Essa distinção matemática, sutil, é exatamente o tipo de detalhe que costuma ser feito errado na maioria dos sistemas, e aqui foi feito certo.

A identidade experimental do projeto também segue rigorosamente a receita da seção 1.4: existem três identidades distintas para composição, execução e experimento, e a identidade de composição foi deliberadamente ampliada para incluir o texto do prompt e as políticas de aprovação — porque dois agentes que diferem apenas no texto do prompt são, de fato, agentes diferentes, e fingir que compartilham identidade destruiria qualquer comparação futura entre eles.

### 2.3 Onde a arquitetura ainda limita a ambição

O primeiro ponto de tensão está na forma como uma composição de agente é hoje declarada. A estrutura atual assume um formato fixo: um único planejador, um único gerenciador de contexto, um único mecanismo de memória, um único portão de avaliação, e uma lista de ferramentas. Isso descreve perfeitamente um agente de codificação clássico, no estilo observar-propor-agir. Mas não existe, hoje, um lugar natural para declarar um sistema de debate entre múltiplos proponentes, um laço de crítica e revisão com dois componentes de julgamento distintos, ou uma busca em árvore com políticas separadas de expansão, avaliação e seleção. Nenhum desses casos exige um motor novo — todos são, em essência, topologias de delegação mais política, exatamente como descrito na seção 1.5 — mas hoje eles só poderiam ser implementados escondidos dentro de um único componente monolítico, o que é precisamente o resultado que a visão do projeto pretende evitar. A correção natural é substituir o formato de posições fixas por um grafo nomeado de componentes, onde os nomes que hoje são obrigatórios passam a ser apenas uma convenção usada pelo primeiro pacote de domínio, não uma imposição da arquitetura.

O segundo ponto de tensão é ainda mais fundamental: hoje, apenas o motor de execução tem permissão para delegar — criar um agente filho. Um componente de planejamento não tem esse poder. Isso significa que qualquer algoritmo cuja própria estrutura seja recursiva — busca em árvore, decomposição hierárquica, delegação condicionada a resultado — não tem hoje onde morar dentro do sistema, exceto dentro do próprio motor, que é exatamente o resultado que se quer evitar segundo a lição da seção 1.6. A generalização natural, alinhada à filosofia de que autoridade deve ser mediada e não apenas concedida por confiança, é tratar a delegação como mais um efeito mediado pelo núcleo de autoridade — um planejador só pode delegar se essa capacidade lhe foi explicitamente concedida na composição, e cada delegação continua sendo verificada, orçada e registrada exatamente como qualquer outro efeito privilegiado hoje já é.

O terceiro ponto de tensão diz respeito diretamente à pergunta que motivou esta investigação: como tornar as garantias de proteção do sistema opcionais sem enfraquecer a arquitetura. A resposta correta, alinhada à lição da seção 1.7, não é escolher entre "sempre protegido" e "nunca protegido" — é distinguir claramente entre **ausência declarada** e **falsificação**. Uma composição pode legitimamente dizer "esta execução não terá avaliação exterior" ou "este componente não passará pelo sandbox mais restritivo" — e o sistema deve aceitar essa declaração, registrá-la como parte da identidade da composição, e marcar qualquer execução resultante como não-atribuível para fins de promoção ou comparação futura. O que nunca pode acontecer, sob nenhuma composição, é um veredito não assinado sendo aceito como se fosse legítimo, ou um evento privilegiado sendo escrito por quem não tem autoridade para escrevê-lo. Essa distinção — desligar é permitido, forjar nunca é — preserva toda a flexibilidade que a visão do projeto pede, sem tocar no pequeno núcleo que precisa permanecer absolutamente não-negociável.

Um quarto ponto, mais técnico e menos filosófico: a promessa de que muitos agentes lógicos podem futuramente compartilhar um número muito menor de processos de execução reais — a base de qualquer escalonamento futuro de alta performance — ainda não foi testada da forma mais exigente possível. A prova que realmente decide essa questão é conseguir suspender uma execução no meio de um turno, reconstruí-la inteiramente a partir do registro de eventos em um processo novo, e retomá-la até a conclusão. Essa prova é barata de se produzir agora e cara de se descobrir ausente mais tarde, quando o sistema já tiver múltiplos pacotes de domínio construídos sobre a suposição de que a reconstrução funciona.

### 2.4 Onde o processo de desenvolvimento está desequilibrado

Vale registrar também uma observação sobre o próprio processo de construção, não apenas sobre a arquitetura final. A fase do desenvolvimento dedicada a provar a espinha de confiança — autoridade, estado, evidência — recebeu um rigor de teste e um número de critérios de falsificação muito superior ao que foi reservado para a fase seguinte, dedicada a provar que o sistema de plugins realmente funciona de ponta a ponta. Isso é compreensível, porque a espinha de confiança é o que sustenta tudo o mais e precisava vir primeiro. Mas é exatamente a segunda fase que prova, ou refuta, a promessa central de que o sistema é de fato um substrato composável — e ela está, hoje, recebendo proporcionalmente menos escrutínio do que merece, justamente no momento em que essa prova é mais necessária.

Por fim, um segundo pacote de domínio — algo fora da codificação, ainda que simples — deveria ser tratado não como um extra desejável, mas como o teste definitivo da promessa de neutralidade de domínio do núcleo: só quando um domínio completamente diferente puder ser adicionado sem qualquer alteração no núcleo é que a alegação de generalidade deixa de ser uma tese e passa a ser um fato demonstrado.

### 2.5 Síntese final

A teoria do primeiro capítulo oferece um critério simples para julgar qualquer arquitetura agêntica: ela separa autoridade de estratégia, mantém o juiz inalcançável, trata delegação como uma única primitiva atenuada, e produz evidência rica o suficiente para ser aprendida no futuro? O projeto Vanguard/AETHER responde sim a cada uma dessas perguntas nos seus fundamentos. O trabalho que resta não é reabrir essas decisões — é terminar de construir a superfície de composição que finalmente deixa qualquer desenvolvedor expressar, sobre essa base sólida, as mesmas formas de agente que a teoria promete serem possíveis: busca, debate, crítica, decomposição hierárquica e, eventualmente, sistemas que aprendem a partir dos próprios rastros de execução que o núcleo, desde o primeiro dia, foi desenhado para nunca deixar mentir.