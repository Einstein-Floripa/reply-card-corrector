# **Introdução**

A execução de simulados em cursinhos populares preparatórios para vestibulares se mostra como sendo um excelente recurso didático, preparando alunos para a situação da prova e ajudando-os a testar seus conhecimentos ao longo do ano de estudos e avaliando seu progresso neste período.

No entanto, a correção destes se mostra algo complexo e demorado, visto que a necessidade de se usar um cartão resposta compatível com os das provas é necessário para um melhor resultado, e tais cartões são pensados para serem corrigidos automaticamente, não por olhos humanos.

Tendo isso em vista, este projeto visa a construção de uma forma automatizada de correção de cartões resposta, visando economizar o tempo dos voluntários envolvidos na correção e otimizar o tempo para tal.

# **Planejamento inicial**

## **As imagens**

Primeiramente a idéia era, buscando uma  operação com custos muito reduzidos, utilizar uma webcam de qualidade considerável para obter imagens dos cartões resposta e utilizar de recursos de visão computacional para fazer a leitura dos pontos preenchidos pelos alunos. No entanto, os primeiros problemas encontrados foram quanto a imagem obtida com uma webcam.

As imagens captadas por uma webcam de qualidade razoável ainda sofrem muitas distorções de cor por conta da iluminação, e tais distorções aumentam a complexidade ao definir um threshold adequado. 

Possivelmente há formas de montar uma câmara de ambiente controlado capaz de dar bons resultados, no entanto a falta de praticidade em fotografar cartão por cartão foi um motivo para procurar outra alternativa. No caso deste projeto, a alternativa escolhida para obter boas imagens dos cartões com uma velocidade boa, foi utilizar um scanner comum.

## **Linguagem**

A linguagem escolhida para o projeto foi python, por conta da simplicidade do código e bindings  eficientes para a [OpenCV](https://opencv.org), biblioteca de visão computacional escolhida.

## **A biblioteca**

A OpenCV é uma biblioteca para  visão computacional muito consolidada, robusta e com diversos recursos. Implementada em C/C++, possui bindings para diversas linguagens. Aqui cabe um ponto interessante deste projeto, de que considerando que a linguagem escolhida tem diversas outras bibliotecas de visão computacional, é possível que a utilização da OpenCV tenha sido um "overkill", por conta da minúscula fração de recursos da biblioteca utilizados.

# **O algoritmo**
        
Está é a seção mais importante deste processo, onde serão descritos os passos executados no processamento de cada cartão-resposta (de forma genérica, desconsiderando as diferenças entre os modelos de prova propostos).

## **Conceitos importantes**

Para uma melhor compreensão da descrição do processo que virá a seguir, alguns conceitos são importantes para garantir o entendimento dos termos.

* **Imagem**
  
    As imagens lidas pela OpenCV são simplesmente matrizes, onde cada elemento da matriz é um vetor com 3 valores (BGR). Ex: 
    
    Vermelho -> ` (0, 0, 255)`
    
    Azul -> ` (255, 0, 0)`
    
    Verde -> `(0, 255, 0)`
    
    Magenta -> `(255, 0, 255)`

    Ponto importante sobre as imagens processadar com a OpenCV em python é que a os bindings são utilizados necessariamente com a biblioteca NumPy para um melhor desempenho no processamento das matrizes.

* **Máscara binária**
   
     Uma máscara binária é uma imagem onde cada pixel da imagem tem apenas um valor, que pode ser  0 ou 255.

* **Contornos**
    
    Contornos são conjuntos de pontos que delimitam objetos detectados na imagem. Os contornos na OpenCV são encontrados a partir de máscara binárias, e  são traçados nos limites entre os pixels 255 e 0, e para encontrar diferentes conjuntos de contornos, utilizam-se diversos métodos para criar as máscara binárias.

* **Threshold**
    
    Um threshold é um limite utilizado para classificações.

## **Primeiro passo: a organização da pasta**
        
Ao se deparar com a raiz deste repositório, nota-se uma divisão em pastas para cada modelo de cartão resposta. Isso se deu por conta da sequência de desenvolvimento, onde cada cartão resposta  foi desenvolvido a parte. 

Cada pasta é um executável de python, que fará a leitura dos cartões e organizará os dados. Dentro de cada pasta, tem 3 pastas:

* scans
  
  Pasta é onde o algoritmo procurará as folhas a serem lidas

* info

  Pasta para as tabelas. Uma tabela intermediária, chamada `data.csv` armazenará os dados lidos entre a execução de dois módulos do código, `organized_data.csv` armazenará os dados finais processados e `subscribers.csv` é o arquivo onde o código buscará pelos inscritos no simulado para serem linkados a suas provas.

* results
 
  Pasta para armazenas dados sobre cada cartão individualmente. Subdivida em duas pastas, onde uma é destinada as leituras feitas com sucesso (i.e. o código foi capaz de identificar o preenchimento de um CPF para linkar a um aluno inscrito), com arquivos `.png` para salvar as leituras de cada inscrito e `.txt` para salvar  os logs de cada leitura, para que um debug posterior possa ser feito, a fim de reconhecer as falhas do algoritmo ou as falhas de preenchimento encontradas.
  
  As falhas são armazenadas em outra pasta, e salvam além da imagem escaneada e do log de erros, um `.csv` com as respostas lidas do cartão sem CPF identificável. Isto é para facilitar que o operador humano consiga efetuar a linkagem de forma manual a fim de possibilidar um feedback sobre o simulado para o aluno.

## **Segundo passo: a execução**

Inicialmente algumas variáveis para a organização das pastas fazerem sentido são criadas. O programa cria o arquivo de saída se este  não existir e escreve seus headers. As samples são obtidas a partir de todos os arquivos da pasta `scans`que tiverem em seu nome a palavra `scan`, e este detalhe foi feito assim por conta do scanner utilizado pelo projeto, em que o nome padrão das imagens escaneadas são `scanXXXX.jpg`.

Então, para cada imagem, os seguintes passos são executados:

* **Correção do sentido da  folha:**
  
  O scanner utilizado possui um leitor para múltiplas folhas, que podem ser posicionadas em uma entrada do dispositivo e são escaneadas uma a uma. Se uma etapa não verificar se a folha está no sentido certo (com o cabeçalho "para cima"), uma falha no empilhamento das folhas causaria erros de leitura e uma invalidação do cartão resposta. Os  [cartões resposta desenvolvidos](./reply_card_models "Link para os modelos de cartão resposta") possuem um retângulo grande na parte superior. 
  
  São obtidos os contornos da imagem com uma máscara binária a partir de um threshold superior e inferior, tomando-se os valores entre os limites como uma classe e os demais como a segunda (nesse projeto praticamente todas as máscara binárias são criadas a partir da função `cv.inRange` com dois limites inferior e superior). É selecionado dentre os contornos o maior contorno que esteja posicionado abaixo dos 1/14 da folha ou acima dos 13/14. Se  o contorno for encontrado na parte de cima, não se modifica nada, caso contrário, utiliza-se a função `cv.rorate` para ajustar a folha.

* **Correção de perspectiva e correção fina de ângulo**:

  Para o método de leitura que será utilizado, é necessário que a folha esteja sempre com o mesmo tamanho, com perspectiva alinhada e o mais perfeitamente alinhada possível. Para tal, as folhas tem marcações quadradas nas 4 extremidades que necessitam ser detectados. O processo foi feito de forma análoga a descrita anteriormente para a localização do retângulo de orientação, e após os contornos dos quadrados serem localizados, são utilizados os pontos extremos referentes ao canto de cada quadrado (Ex: do quadrado que marcar o canto superior esquerdo, é utilizado o ponto superior esquerdo) para formar um grande retângulo, que é usado de fonte e é ajustado a um retângulo regular criado com base nos mesmos pontos. É utilizada a função `cv.getPerspectiveTransform` para obter a matriz de transformação e a função `cv.warpPerspective` para ajustar a área fonte ao retângulo destino. A imagem ajustada é ainda redimensionada para  um tamanho pré definido de 1017 pixels de largura para 1401 de altura. Estas medidas não tem nenhum motivo em especial, foram definidas empiricamente para obter uma tolerância razoável a erros nas etapas que se seguem.

* **Obtenção das posições de cada item a ser lido**
  
  Com a imagem ajustada aos quadrados e redimensionada, de maneira empírica as posições de cada campo a  ser preenchido são mapeadas nas funções `get_response_pos` e `get_cpf_pos` e usadas nas funções `read_response` e `read_cpf`, que leem as os cammpos, diferenciando campos sem preenchimento e preenchimento duplo, e retornando junto às respostas um log de erros para ser salvo e usado posteriormente em correções manuais ou feedbacks. Além das respostas e do cpf, é lido o dia da prova para organização posterior dos dados. Para o mesmo propósito, as áreas analisadas para leitura são desenhadas na imagem do cartão a ser salvo.

* **Armazenamento da leitura**

  Essa etapa apenas faz a leitura dos dados e os salva no arquivo `info/dava.csv` os sucessos e cada falha é armazenada separada em subpastas da pasta `results/failures`, assim como os logs, que são armazenados em texto nomeados com o CPF ao qual são vinculados.

* **Organização dos dados**
  
  Após o script principal ler os dados, um segundo é chamado. Este abre as tabelas `info/data.csv` e `subscribers.csv`, relaciona os CPFs lidos com os CPFs inscritos e cria  uma nova tabela, na qual os dados estão organizados de maneira previamente definida junto ao departamento de Inteligência, para que sejam corrigidos e gerem feedbacks para os alunos.

# **Próximos passos**

Atualmente o projeto é executado por uma linha de comando, necessitando um certo nível técnico do usuário. Os próximos passos, em ordem de prioridade serão:

* Fazer deploy do projeto em uma plataforma intuitiva e simplificada
* Fazer um script que lerá os dados e gerará PDFs com os feedbacks a serem passados aos alunos