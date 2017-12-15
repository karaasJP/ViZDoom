from vizdoom import *
from time import sleep
def replay(team):
    game = DoomGame()
    game.load_config("../../scenarios/cig.cfg")
    # At this moment ViZDoom will crash if there is no starting point - this is workaround for multiplayer map.
    game.add_game_args("-host 1 -deathmatch")

    game.init()

    # Replays episode recorded by player 1 from perspective of player2.
    game.replay_episode("multi_rec.lmp", team)

    while not game.is_episode_finished():
        game.advance_action()


    print("Game finished!")

    game.close()

#ここで再生する番号を選択0~７まで？
replay(3)
