### Configurations and Environments
This application relies on two forms of application configuration, a config.py that sets certain variables depending on whether or not the user has debug mode enabled, and the .env that has all of the secrets for the application. The config.py has the following variables:

#### Debug
- VERIFICATION_INPUT: Shows an HTML file that has an input box for the flag, and the JS code to accompany submitting the flag to the verify endpoint. Disable if you want the user to submit their own manual post requests
- PARAMETERIZE: Weather or not to parameterize the flag, even if the parameterize function is called. This is so that application function can be altered without altering the code of the level itself.
- GAMES: A dictionary that is initialized as dict(). This stores game data when the application is first created, and is what makes the application so dynamic. This should be left as is.
- URL: This is the base URL for your application. It is used for all of the routes and redirects, so if it is set wrong the application will not function. In debug mode the default URL will work, and your app should be deployed on the same port as is in the URL
- TEMPLATE: The name of the template HTML file for each of your games. This template should be in src/static/templates
- LLM: Toggle for LLM integration. If this is set to True, your LLM key in .env must be set.
- MONGO: Toggle for Mongo integration. If this is set to True, your Mongo URL and database name must be set in the .env
- BASE_DIR: Does not need to be changed, resolves to the "app" directory for the finding of solutions and prompts
- SOLUTION_EXTENSION: The extension of your solution files so that you can have multiple kinds of files in your solutions folder
- ADMIN_CODE: Weather or not to require an admin code to access the deployed site and get a cookie. If this is enabled, users must have an admin code assigned to them at user creation (use admin portal)

#### Production
Allows for the overwriting of URL, LLM, and MONGO, for easy deploying from development. You could also toggle the template if you desire. 

#### Environment (dotenv)
- AES_PASSWORD: String of text that is used for the encryption password and by extension parameterization
- KEY: LLM token
- MONGODB_URL: Connection string for MongoDB
- DATABASE_NAME: Name of your database in MongoDB
- SESSION_SECRET: Used for passing application secrets from frontend to backend

### Imports
The following are all of the FastAPI imports that you should need to operate the application. 
* Request is the required argument for any route in FastAPI
* Response is a response object for simple responses
* Redirect is an object that redirects users to another page
* HTMLResponse returns an HTML response object
* JSONResponse returns a JSON response object

```python
from fastapi import Request, Response
from fastapi.responses import RedirectResponse, HTMLResponse, JSONResponse
```
Import the preloaded templates from extensions so we have access to all of our templates. 
```python
from app.utils.extensions import templates
```

For included functions and class imports, please visit the Templates, Classes, and Functions section.

### Configuration
Get the configuration, this is based on weather or not the application is created with debug True or False.
```python
config = get_config()
```
If env variables are needed, (they should not be since they should be used in the helper classes) they can be included with dotenv, and used with os.getenv().
```python
from dotenv import load_dotenv
load_dotenv()
your_variable = os.getenv("YOUR_VARIABLE")
```
### Setting functions and variables
Set the default hint string. This is optional.
```python
default_hint = "This is a default hint"
```
Create the game class, with the default "is_game" unchanged. This will create a new game as opposed to a new game. We pass the default hint to this game, and the name "Never Trust Your Eyes". This will create the route for the game as "/game/never_trust_your_eyes". 
```python
game_class = Page("Never Trust Your Eyes", default_hint=default_hint)
```
Here we create our own instructions function that returns our own template. Button HTML is generated with the generate_button function, where we pass the text that is in the button, and the URL that the button will redirect the user to. We than return the template to the user with the following arguments:
* name: The template that we are returning to the user. This specific template is defined in the config as game_template.html.
* request: A mandatory argument from FastAPI, just pass the mandatory request variable of the function.
* context: The text that is being passed to the template, please visit the Templates, Classes, and Functions section for possible arguments.
* status_code: Optional status code to pass, 200 is success.
```python
async def instructions(request: Request):
    text = ("You've been tasked with pen testing a companies backend API. You know this company has a history "
                    " of using the bad practise of 'Security through Obscurity'. "
                    "Click the button below and look around "
                    "for anything that could grant you access. The endpoint is in perfect working order!")

    button = generate_button("Frontend", f"{config.URL}{game_class.url_prefix}/frontend")

    return templates.TemplateResponse(name=config.TEMPLATE, request=request, context={"header": game_class.name,
                                    "text": text, "primary_button": button}, status_code=200)
```
Instead, you could also just create instruction text, and it will automatically return the default template with the text in the "text" field of the template.
```python
instructions_text = ("You've been tasked with pen testing a companies backend API. You know this company has a history "
                    " of using the bad practise of 'Security through Obscurity'. "
                    "Click the button below and look around "
                    "for anything that could grant you access. The endpoint is in perfect working order!")
```
Create a super simple verify function that checks the request headers and sets success to True or False:
```python
async def verify(request: Request):
    return {"success": request.headers.get("Authorization") == "YouWillNeverGuessMe"}
```
You could also create a more complex verify function that customizes your error message and code:
```python
async def verify(request: Request):
    if request.headers.get("Authorization") == "YouWillNeverGuessMe":
        return {"success": True}
    else:
        return {"success": False, "error": {"text": "Unauthorized", "code": 403}}
```
You than set these functions in the class so they can be used in the route. If the functions are not set the routes will not be created, and the game will not work properly.
```python
game_class.set_functions(instructions=instructions, verify=verify)
```
Additionally, if you have set instructions as text instead of a function, it works the same way:
```python
game_class.set_functions(instructions=instructions_text, verify=verify)
```
Set game as the game_class.route. This makes it more simple to add routes, and shorter inputs in the __init__ to create the route.
```python
game = game_class.route
```
### Create your own routes
Create a frontend route that passes the header for the user to sniff and exploit the level. The frontend is a special route that will show the hint button, and will allow the user to get hints. Other routes will not.
```python
@game.get('/frontend', response_class=HTMLResponse)
def check_headers(request: Request):
    return templates.TemplateResponse(request=request, name=config.TEMPLATE, status_code=403, headers={"Password": "YouWillNeverGuessMe"})
```
More complex frontend functions can be created from the other template arguments such as the one below. This frontend function takes arguments, sets cookies, and uses custom functions for the specific level to create its own return object with objects such as a table. 

```python
@game.get('/frontend/{page_num}', response_class=HTMLResponse)
async def serve_frontend(request: Request, page_num: str):
    cookie = request.cookies.get("cookie", None)
    return_text = "You do not have a cookie set, please refresh the page"
    if cookie is None:
        response = templates.TemplateResponse(request=request, name=config.TEMPLATE, context={"header": return_text})
        response.set_cookie("cookie", generate_cookie())
        return response
    else:
        stripped, prepended, appended = get_page(cookie)
        if stripped == page_num:
            return_object = generate_html_text(complete=True, prepended=prepended, appended=appended)
        else:
            logger.log(f"{page_num} is not {stripped}")
            return_object = generate_html_text()

    return templates.TemplateResponse(request=request, name=config.TEMPLATE, context=return_object)
```

_The bulk of the code for this demonstration is pulled from leaky_header in the routes folder of the Github._