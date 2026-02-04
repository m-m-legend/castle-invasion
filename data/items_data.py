WEAPONS = {
    "espada": {
        "name": "Espada",
        "damage": 10,
        "type": "melee"
    },
    "escudo": {
        "name": "Escudo",
        "damage": 5,
        "type": "defense",
        "block": 0.3 
    },
    "lanca": {
        "name": "Lança",
        "damage": 12,
        "type": "melee"
    },
    "cajado_mago": {
        "name": "Cajado do Mago",
        "damage": 15,
        "type": "magic",
        "boost": 1.2
    },
    "arco_flecha": {
        "name": "Arco e Flecha",
        "damage": 11,
        "type": "ranged"
    }
}


HEALS = {
    "biblia": {
        "name": "Bíblia",
        "heal_multiplier": 1.1,
        "enemy_damage_multiplier": 0.3,
        "cooldown": 2,
        "message": "O senhor é meu pastor, e nada me faltará...",
        
    },

    "semente_regeneradora": {
        "name": "Semente Regeneradora",
        "heal_multiplier": 1.2,
        "enemy_damage_multiplier": 0.1,
        "cooldown": 2,
        "message": "Você sente sua vida se regenerando...",
        
    }
}

ITEMS = {"chave_quadrada":{
    "name": "Chave Quadrada",
    "description": "Uma chave de formato quadrado, usada para abrir cadeados especiais.",
    "type": "key",
    "usage": "Abre portas ou baús especiais que requerem uma chave quadrada."
},
         "pocao_cura":{
    "name": "Poção de Cura",
    "description": "Uma poção que restaura 50 pontos de vida.",
    "type": "consumable",
    "health_restore": 50
         }}
