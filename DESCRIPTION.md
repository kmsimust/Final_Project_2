# Description
    Turn Based RPG game inspired by pokemon and RPG-maker Games. With a maximum of 4 characters on the player side to fight with other people. The player can walk around to find another npc to fight off in a glorious 4v3 pokemon-like battle. In combat, players can choose between attack and defense. Also each pokemon have ability to choose.

# File overview:
    main          : as it name said it the main loop of the game.
    settings      : the game setting, contains width, height, and colors.
    support       : the function used for loading image and organize into dict.
    clock         : timer
    sprites       : make use of pygame sprite, use to render the game components.
    groups        : use to draw sprite by its layer order.
    menu          : solely for changing game loop to main menu.
    inventory     : use to checking player team and its content.
    dialog        : when interact with NPCs this file will be use.
    data_part     : solely to record combat data into csv.
    battle        : heart of combat part.
    battle_entity : making pokemon into objects for managing.
    battle_aux    : incomplete function for battle_entity.

    attack_data     : contains the attacks data.
    bchar_data      : contain pokemon data for battle.
    character_data  : contain NPCs data.
    effects_data    : imcomplete data for battle_aux.
    