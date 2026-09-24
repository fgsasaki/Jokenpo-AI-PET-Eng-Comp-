# main.py
import modo_ia
# import modo_pvp  # <-- Comentado por enquanto, até a equipe terminar

def menu_principal():
    while True:
        print("\n" + "="*30)
        print("   JOKENPO VISION - PET ENG   ")
        print("="*30)
        print("1. Jogador vs IA Preditiva")
        print("# 2. Jogador vs Jogador (PvP) [EM DESENVOLVIMENTO]")
        print("3. Sair")
        print("="*30)
        
        escolha = input("Digite o numero da opcao desejada: ")
        
        if escolha == '1':
            print("\nIniciando modulo de Inteligencia Artificial...")
            modo_ia.iniciar_jogo_ia()
            
        elif escolha == '2':
            print("\n[!] O modo PvP ainda esta em desenvolvimento pela equipe!")
            # modo_pvp.iniciar_jogo_pvp() # <-- Comentado para não dar erro
            
        elif escolha == '3':
            print("Encerrando sistema...")
            break
        else:
            print("Opcao invalida. Tente novamente.")

if __name__ == "__main__":
    menu_principal()