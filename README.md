# Operação Titânio: Robôs vs Zumbis

Bem-vindo à **Operação Titânio**, um jogo de plataforma em 2D onde você controla robôs defensores para combater uma invasão zumbi mecânica!

---

## 📖 História

Em **Operação Titânio**, um grupo de robôs de patrulha é enviado para limpar as plataformas externas da Estação Verde, que foi invadida por zumbis mecânicos. Os zumbis escaparam de um setor de testes de IA e agora rondam áreas delimitadas, avançando lentamente sobre as passarelas.

Sua missão é simples e direta:

1. Avançar pelas plataformas da estação, utilizando saltos precisos para evitar quedas;
2. Eliminar todos os zumbis mecânicos para liberar o portal de saída e completar o nível.

É preciso derrotar cada zumbi dentro da área de patrulha para que o portal seja ativado. Só então você pode avançar para o próximo estágio.

---

## 🤖 Personagens

- **R-01 Guardião**: Robô tanque de elite com blindagem reforçada. Movimenta-se com esteiras, enfrenta zumbis mecânicos e protege as passarelas.

  - **Idle**: LEDs de escaneamento piscando.
  - **Andar**: Esteira de tração em movimento.

- **Z-Mec**: Zumbi mecânico padrão, animado por circuitos corrompidos. Patrulha um trecho fixo da plataforma.

  - **Idle**: Engrenagens enferrujadas girando lentamente.
  - **Andar**: Passos mecânicos cadenciados.

---

## 🎮 Como Jogar

1. **Menu Principal**

   - **Iniciar Jogo**: Comece sua missão.
   - **Música On/Off**: Alterna música de fundo.
   - **Sair**: Fecha o jogo.

2. **Controles**

   - **← / →  ou A / D**: Movimentar o robô.
   - **⬆ ou W **: Pular 
   - **Colisão**: Toque em um zumbi e você perde vida.

3. **Objetivo**

   - Elimine zumbis enquanto avança.
   - Restaure o gerador ao chegar ao portal de saída, pegando a bandeira.

---

## ⚙️ Instalação e Execução

1. **Instale PgZero**:
   ```bash
   pip install pgzero
   ```
2. **Clone o repositório**.
3. **Organize os assets**:
   - `images/`: sprites dos robôs e zumbis
   - `sounds/`: efeitos (por exemplo, `jump.wav`)
   - `music/`: trilha sonora (`background.mp3`)
4. **Execute**:
   ```bash
   pgzrun main.py
   ```

---

## 📂 Estrutura do Projeto

```
root/
├── images/       # Sprites (PNG)
├── sounds/       # Efeitos sonoros (WAV)
├── music/        # Música de fundo (MP3)
├── main.py       # Código-fonte do jogo
└── README.md     # Descrição e instruções
```

---

## 📝 Licença

Este projeto está licenciado sob a **MIT License**. Sinta-se à vontade para usar e modificar!

