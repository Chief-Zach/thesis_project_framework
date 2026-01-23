from app.utils.game_setup import Pages_Object
# Import all of your games here. Be sure to import the "game_class" or whatever you choose to name it
from levels.welcome_game import welcome_game
from levels.hard_hashing import game_class
# from .levels.my_next_game import my_next_game

def my_pages():
    # Leave this here
    my_games_list = Pages_Object()

    # You then create your games here. The order of your games/pages matter.
    # Put all of your "non-games" at the front to ensure no cross over.
    # Register the rest of your games in the order you want users to play them
    my_games_list.append(welcome_game)
    my_games_list.append(game_class)
    # my_games_list.append(my_next_game)
    # Leave this here
    return my_games_list

