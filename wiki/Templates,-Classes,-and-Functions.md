# Templates
## game_template.html
### Arguments
*All arguments are optional but passing no arguments will result in an empty page. All arguments are HTML safe, meaning you can create your own HTML for each passed argument*

* **header**: The header text on the left side of the page. Classes: display-5 fw-bold text-body-emphasis
* **table**: Table displayed below the header. Classes: None
* **text**: Regular text. Classes: lead mb-4
* **form_data**: Form data displayed allowing for forms such as login pages.
* **result_text**: Text with the id of result. This can interact with buttons. Classes: lead mb-4 id: result
* **subtext**: Slightly greyed out subtext. Class: mb-4
* **hidden_text**: Allows for the injection of anything into the template. Meant for hiding text in the page that users can find.
* **primary_button**: Blue primary button in a div for centring. Works with create_button function, but you could create your own HTML
* **secondary_button**: Grey secondary button in a div for centring. Will display to the right of primary button in line when both are present
* **right_content**: All the content that appears below the "Hint" header tag. You can find the default hint HTML in the /hint route in the Page class
* **scripts**: Inject the JS scripts needed for clientside communication into the page. This is done through the page class with `game_class.load_scripts` and `game_class.scripts["script_name"]`
## game_template_verify.html
Same arguments as game_template.html, but it will also include an input form for submitting flags, and the JS code to allow the form to function. These files are separate so that if the designer wishes to obfuscate the verify route, they may without revealing its source in the client side code. 

## how_to.html
This template takes no arguments. Custom made for the how to page.

## welcome.html
This template takes no arguments. Custom made for the welcome page. 

# Classes
## Page
This is the main class that creates each page on the website. Other than the root page, every page on the example site is generated with this class.
### Arguments
* **name: str**: Name of the level. The name creates the URL endpoint through lowering it, and replacing spaces with _.
* **instructions: string or function**: Instructions as a string to be put in the basic instructions function, or define your own instructions HTML and return your own template
* **verify: function**: A function that returns a dict with a success flag like {"success": True} or {"success": False}. If success is false, you can also return a nested error dict such as {"success": False, "error": {"text": "Unauthorized", "code": 403}}
* **scripts Dict[str, str]**: A dictionary of js files as values, and your name (does not have to match filename) for the file. This allows you to define all the scripts once per route, and use them in FastAPI context like: 
```python
return templates.TemplateResponse(request=request, name=config.TEMPLATE, 
    context={"scripts": game_class.scripts["connection"],
    "header": "Post Here!", "primary_button": button})
```
* **default_hint: str**: The default hint string if there is no AI or database hookup
* **is_game: bool**: This changes the route URL for the route that is created. If is_game is true the route is /games/{name}, otherwise its just /{name}

* **filename**: Filename (without extension) for the LLM hint. This is optional and will default to the string name
* **** 

### Functions
* **set_index**: Setter method to set class index, used in route creation
* **set_functions**: Sets the instruction and verify functions if they were not ready by the time Page creation was needed, for example if a route string needed to be accessed to create verify or instruction functions:

```python
    button = generate_button("Frontend", f"{config.URL}{game_class.url_prefix}/frontend")
```
* **success**: Registers in the database that the user has completed the level, and returning the user a success message, along with the URL of the next game
* **load_scripts**: Setter method for the scripts variable in the class
* **get_scripts**: Gets you the script that you loaded with load_scripts. Can use this instead of a dictionary lookup
This class takes the arguments of name (string), instructions (string or function), verify (function), scripts()

## Database Config
This is the class that creates the connection to MongoDB for user of tracking user progress, and enabling AI hints. This simple class reads in the MongoDB URL provided in the .env, and the name of the database where user and level data is stored. This class also makes a call to initiate the Beanie database, therefore setting up the User document defined in the next class.

## User Document
The User document, as well as its helper base models (Hint and Level), create an efficient and simple way for the application to interact with MongoDB. All indexes, both unique and sorting, are automatically created with the first interaction with the Mongo collection, meaning the only thing developers need to do is create a database, add the URI and the database name to the env, and {NAME} will create the collection and index's. If you would like to add more data to the collection, or collect less user data, it is as easy as adding or removing fields from the User class.

### Functions
This class contains a variety of helper functions for interacting with the table.

#### Class Methods
*These take a cookie string or a User dictionary*
* **get_user**: Get the user object from a user cookie string
* **get_user_by_code**: Get the user object from their user access code
* **generate_leaderboard**: Generate the HTML for a leaderboard of all users in the database
* **create_level**: Creates a fresh Level object and returns it
* **upsert_hint**: Upserts a hint for the current level from a cookie string
* **create_user**: Creates a user object from a pre generated cookie string

#### Self Methods
*For these, objects of User must be passed, not just a dict*
* **get_hint_length**: Gets the number of hints the user has got for the current level, from the Level string
* **complete_level**: Sets level_completed to True from a level string, from a user object
* **upsert_hints_user**: Upserts a hint from the current level from a level string from a Level string
* **get_last_hint**: Gets the last from the hint string
* **is_complete**: Checks if a level is complete by passing the Level string

## SHA256Service
### Functions
* **hash**: Hash a string

## AESService
### Functions
* **encrypt**: Encrypt bytes and return a string
* **decrypt**: Decrypt encrypted bytes

## Parameterization
Handles parameterized flags based on the inputted user cookie and any other arguments

### Functions
* **parameterize_flag**: Takes in a user cookie (string) and any other arguments and uses them to create a parameterized flag
* **parameterize_with_data**: Takes in the user cookie and the data in dictionary form you would like to hide (and later access)
* **get_data_from_parameterization**: Takes in the encrypted data and decrypts it, returning you a dictionary object of the data

## Table
Creates the HTML for a table from a dictionary or list of data, with an optional separate header list.

## LLM Service/Manager
Handles all functions when it comes to the LLM interaction. The developers of new levels should use llm_manager.py to get the instances of the LLM that they want via the config file. If a developer wants to add another possible model in, such as Ollama integration, the llm_service.py should be changed to allow for this new model to be called from the manager.

* **get_llm**: Get the instance of the LLM class of your choice based off of the config
* **get_hint**: Get a hint based on the prompt and the users past queries

### Functions
* **get_html**: Returns the table HTML

# Functions (in extensions.py)
* **get_cookie**: Returns the user cookie if there is one, otherwise return None 
* **generate_user_cookie**: Generates a new user cookie (made from uuid4), creates a new user from that cookie, and returns that new cookie
* **quote_string**: Wrap a string in double quotes (for HTML generation)
* **generate_button**: Generate the HTML for primary and secondary buttons with optional links and element ids with bootstrap classes


