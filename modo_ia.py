"""
MÓDULO DE INTELIGÊNCIA ARTIFICIAL - JOKENPÔ VISION
Implementação de Cadeia de Markov Estocástica
"""

import json
import os
import random

class IAPreditiva:
    def __init__(self, arquivo_memoria="memoria_ia.json"):
        self.arquivo_memoria = arquivo_memoria
        self.memoria = self.carregar_memoria()
        self.historico_recente = []

    def carregar_memoria(self):
        """Carrega a matriz de transição do disco"""
        if os.path.exists(self.arquivo_memoria):
            try:
                with open(self.arquivo_memoria, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return {}
        return {}

    def salvar_memoria(self):
        """Salva a matriz de transição no disco para persistência"""
        with open(self.arquivo_memoria, 'w', encoding='utf-8') as f:
            json.dump(self.memoria, f, indent=4, ensure_ascii=False)

    def aprender(self, jogada_atual):
        """Atualiza as frequências estatísticas baseadas na jogada humana"""
        if len(self.historico_recente) == 2:
            # Padronizado com vírgula para coincidir com o JSON existente
            estado = f"{self.historico_recente[0]},{self.historico_recente[1]}"
            
            if estado not in self.memoria:
                self.memoria[estado] = {"Pedra": 0, "Papel": 0, "Tesoura": 0}
            
            if jogada_atual in self.memoria[estado]:
                self.memoria[estado][jogada_atual] += 1
        
        # Atualiza o histórico de curto prazo (janela deslizante)
        self.historico_recente.append(jogada_atual)
        if len(self.historico_recente) > 2:
            self.historico_recente.pop(0)

    def decidir_jogada(self):
        """Toma uma decisão estocástica baseada nas probabilidades da Cadeia de Markov"""
        opcoes = ["Pedra", "Papel", "Tesoura"]
        contra_ataque = {"Pedra": "Papel", "Papel": "Tesoura", "Tesoura": "Pedra"}

        if len(self.historico_recente) == 2:
            estado = f"{self.historico_recente[0]},{self.historico_recente[1]}"
            
            if estado in self.memoria:
                frequencias = self.memoria[estado]
                pesos = [frequencias["Pedra"], frequencias["Papel"], frequencias["Tesoura"]]
                
                # Sorteia a previsão do humano ponderada pelos pesos estatísticos do JSON
                if sum(pesos) > 0:
                    previsao_humano = random.choices(opcoes, weights=pesos, k=1)[0]
                    return contra_ataque[previsao_humano]

        # Fallback: Se não houver dados suficientes para o estado atual, escolhe aleatoriamente
        return random.choice(opcoes)