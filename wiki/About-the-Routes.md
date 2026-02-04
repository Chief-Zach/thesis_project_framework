# Instructions
The instructions route, present at /games/{name} or /{name} such as /games/welcome_game or /how_to is just the default GET route that can contain some instructions for the game, or just be a regular webpage. The instructions will just create a default route at the name of the page, and you can use a current two panel template such as the how_to.html, or create your own.

# Verify
The verify route, meant only for games at /games/{name}/verify, such as /games/welcome_game/verify, is a POST request that returns a success or failure dictionary. This return is than evaluated by the Page class, and returns the success function if success is True. This success function will than serve the user with the success message, as well as credit them in the database with passing the level. 

# Hint
The hint route meant only for games at /games/{name}/hint, such as /games/welcome_game/hint, and only accessible on the website from the frontend route (below), is a POST request that will return a dictionary with the hint text using the "payload" key. This hint will be the default hint if the LLM is not engaged, or there is no database setup, otherwise it will be an LLM generated hint based on past user requests.

# Frontend
The frontend route is not a required route, nor is it present in the Page class, as there is no useful default setup for this function. This route is important because it is the only route where hints will be shown, and the hints route will be requested by the frontend. It is intended to be used as some sort of real world interface, from a login page, to a "Post Here!" button that makes a web request to the backend. This is where the challenge is supposed to take place.

# Other
You are free to create any more routes that you think would make the user experience better. These routes could be places to make the experience more interactive, or can simulate web requests. You can see how to do this in the tutorial section of this wiki.


**A note about all routes**


_All routes require a cookie to access. This cookie is what differentiates users, and allows for a variety of functions. If a GET request is made to a route without a cookie, the user will be redirected to the home page and assigned a cookie. If a POST request is made to a route without a cookie, the user will receive a malformed request status code, as well as a message to include a cookie._