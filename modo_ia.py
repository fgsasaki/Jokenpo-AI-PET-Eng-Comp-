import json
import os
import random

ARQUIVO_MEMORIA = "memoria_ia.json"

class IAPreditiva:
    def __init__(self, arquivo_memoria=ARQUIVO_MEMORIA):
        self.arquivo_memoria = arquivo_memoria
        self.padroes = self._carregar_memoria()
        self.historico = []

    def _carregar_memoria(self):
        padroes_padrao = {
            "Pedra,Pedra": {"Pedra": 0, "Papel": 0, "Tesoura": 0}, 
            "Pedra,Papel": {"Pedra": 0, "Papel": 0, "Tesoura": 0}, 
            "Pedra,Tesoura": {"Pedra": 0, "Papel": 0, "Tesoura": 0},
            "Papel,Pedra": {"Pedra": 0, "Papel": 0, "Tesoura": 0}, 
            "Papel,Papel": {"Pedra": 0, "Papel": 0, "Tesoura": 0}, 
            "Papel,Tesoura": {"Pedra": 0, "Papel": 0, "Tesoura": 0},
            "Tesoura,Pedra": {"Pedra": 0, "Papel": 0, "Tesoura": 0}, 
            "Tesoura,Papel": {"Pedra": 0, "Papel": 0, "Tesoura": 0}, 
            "Tesoura,Tesoura": {"Pedra": 0, "Papel": 0, "Tesoura": 0}
        }
        if os.path.exists(self.arquivo_memoria):
            with open(self.arquivo_memoria, "r") as f:
                return json.load(f)
        return padroes_padrao

    def decidir_jogada(self):
        if len(self.historico) < 2:
            return random.choice(["Pedra", "Papel", "Tesoura"])
        
        seq = f"{self.historico[-2]},{self.historico[-1]}"
        opcoes = self.padroes[seq]
        prev = max(opcoes, key=opcoes.get)
        
        if opcoes[prev] == 0:
            return random.choice(["Pedra", "Papel", "Tesoura"])
        elif prev == "Pedra": return "Papel"
        elif prev == "Papel": return "Tesoura"
        else: return "Pedra"

    def aprender(self, jogada_usuario):
        if jogada_usuario in ["Pedra", "Papel", "Tesoura"]:
            if len(self.historico) >= 2:
                chave = f"{self.historico[-2]},{self.historico[-1]}"
                self.padroes[chave][jogada_usuario] += 1
            
            self.historico.append(jogada_usuario)
            if len(self.historico) > 2:
                self.historico.pop(0)

    def salvar_memoria(self):
        with open(self.arquivo_memoria, "w") as f:
            json.dump(self.padroes, f, indent=4)