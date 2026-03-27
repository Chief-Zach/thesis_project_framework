from app.utils.game_setup import Pages_Object
# Import all of your games here. Be sure to import the "game_class" or whatever you choose to name it
from levels.welcome_game import welcome_game
from levels.sample_level import password_level
from levels.reflected_xss_post import reflected_xss_post
from levels.rfi_easy import rfi_easy
from levels.broken_auth_password_attacks import broken_auth_password_attacks
# from .levels.my_next_game import my_next_game

def my_pages():
    # Leave this here
    my_games_list = Pages_Object()

    # You then create your games here. The order of your games/pages matter.
    # Put all of your "non-games" at the front to ensure no cross over.
    # Register the rest of your games in the order you want users to play them
    my_games_list.append(welcome_game)
    my_games_list.append(password_level)
    my_games_list.append(reflected_xss_post)
    my_games_list.append(rfi_easy)
    my_games_list.append(broken_auth_password_attacks)
    # my_games_list.append(my_next_game)
    # Leave this here
    return my_games_list

