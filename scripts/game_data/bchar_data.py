BATTLE_CHARACTER_DATA = {
    # player team
    'Player': {
		'stats': {'element': 'normal', 'max_health': 1000, 'max_energy': 100, 'attack': 15, 'defense': 0, 'recovery': 5, 'speed': 1},
        'attack': {0: 'scratch'},
		'abilities': {5: 'spark', 15: 'splash', 20: 'ice', 15: 'ice spike', 25: 'heal', 10:'explosion', 72: 'death ray', 20:'annihilate'},
		'evolve': None},
    'Plumette': {
		'stats': {'element': 'fire', 'max_health': 1000, 'max_energy': 100, 'attack': 5, 'defense': 0, 'recovery': 5, 'speed': 1.5},
        'attack': {0: 'scratch'},
		'abilities': {25: 'heal', 5: 'spark', 5: 'splash', 10:'explosion', 20:'annihilate', 20: 'ice', 25: 'heal'},
		'evolve': None},
        
	# non-player team
	# 'Plumette': {
	# 	'stats': {'element': 'plant', 'max_health': 15, 'max_energy': 17, 'attack': 4, 'defense': 8, 'recovery': 5, 'speed': 1},
    #     'attack': {0: 'scratch'},
	# 	'abilities': {5: 'spark'},
	# 	'evolve': ('Ivieron', 15)},
	'Ivieron': {
		'stats': {'element': 'plant', 'max_health': 18, 'max_energy': 20, 'attack': 5, 'defense': 10, 'recovery': 6, 'speed': 1.2},
        'attack': {0: 'scratch'},
		'abilities': {5: 'spark'},
		'evolve': ('Pluma', 32)},
	'Pluma': {
		'stats': {'element': 'plant', 'max_health': 23, 'max_energy': 25, 'attack': 6, 'defense': 12, 'recovery': 7, 'speed': 1.8},
        'attack': {0: 'scratch'},
		'abilities': {5: 'spark'},
		'evolve': None},
	'Sparchu': {
		'stats': {'element': 'fire', 'max_health': 15, 'max_energy': 17, 'attack': 3, 'defense': 8, 'recovery': 5, 'speed': 1},
        'attack': {0: 'scratch'},
		'abilities': {5: 'spark'},
		'evolve': ('Cindrill', 15)},
	'Cindrill': {
		'stats': {'element': 'fire', 'max_health': 18, 'max_energy': 20, 'attack': 4, 'defense': 10, 'recovery': 6, 'speed': 1.2},
        'attack': {0: 'scratch'},
		'abilities': {5: 'spark'},
		'evolve': ('Charmadillo', 33)},
	'Charmadillo': {
		'stats': {'element': 'fire', 'max_health': 27, 'max_energy': 23, 'attack': 6, 'defense': 17, 'recovery': 7, 'speed': 1.5},
        'attack': {0: 'scratch'},
		'abilities': {5: 'fire', 10:'explosion', 12: 'battlecry', 20:'annihilate'},
		'evolve': None},
	'Finsta': {
		'stats': {'element': 'water', 'max_health': 13, 'max_energy': 17, 'attack': 2, 'defense': 8, 'recovery': 5, 'speed': 1.8},
        'attack': {0: 'scratch'},
		'abilities': {5: 'spark'},
		'evolve': ('Gulfin', 34)},
	'Gulfin': {
		'stats': {'element': 'water', 'max_health': 18, 'max_energy': 20, 'attack': 3, 'defense': 10, 'recovery': 6, 'speed': 2},
        'attack': {0: 'scratch'},
		'abilities': {5: 'spark'},
		'evolve': ('Finiette', 32)},
	'Finiette': {
		'stats': {'element': 'water', 'max_health': 27, 'max_energy': 23, 'attack': 4, 'defense': 17, 'recovery': 7, 'speed': 2.5},
        'attack': {0: 'scratch'},
		'abilities': {5: 'spark'},
		'evolve': None},
	'Atrox': {
		'stats': {'element': 'fire', 'max_health': 18, 'max_energy': 20, 'attack': 3, 'defense': 10, 'recovery': 6, 'speed': 1.9},
        'attack': {0: 'scratch'},
		'abilities': {5: 'spark'},
		'evolve': None},
	'Pouch': {
		'stats': {'element': 'plant', 'max_health': 23, 'max_energy': 25, 'attack': 4, 'defense': 12, 'recovery': 7, 'speed': 1.5},
        'attack': {0: 'scratch'},
		'abilities': {5: 'spark'},
		'evolve': None},
	'Draem': {
		'stats': {'element': 'plant', 'max_health': 23, 'max_energy': 25, 'attack': 4, 'defense': 12, 'recovery': 7, 'speed': 1.4},
        'attack': {0: 'scratch'},
		'abilities': {5: 'spark'},
		'evolve': None},
	'Larvea': {
		'stats': {'element': 'plant', 'max_health': 15, 'max_energy': 17, 'attack': 1, 'defense': 8, 'recovery': 5, 'speed': 1},
        'attack': {0: 'scratch'},
		'abilities': {5: 'spark'},
		'evolve': ('Cleaf', 4)},
	'Cleaf': {
		'stats': {'element': 'plant', 'max_health': 18, 'max_energy': 20, 'attack': 3, 'defense': 10, 'recovery': 6, 'speed': 1.6},
        'attack': {0: 'scratch'},
		'abilities': {5: 'spark'},
		'evolve': None},
	'Jacana': {
		'stats': {'element': 'fire', 'max_health': 12, 'max_energy': 19, 'attack': 3, 'defense': 10, 'recovery': 6, 'speed': 2.6},
        'attack': {0: 'scratch'},
		'abilities': {5: 'spark'},
		'evolve': None},
	'Friolera': {
		'stats': {'element': 'water', 'max_health': 27, 'max_energy': 23, 'attack': 4, 'defense': 17, 'recovery': 7, 'speed': 2},
        'attack': {0: 'scratch'},
		'abilities': {5: 'spark', 15: 'splash', 20: 'ice', 25: 'heal'},
		'evolve': None},
}
