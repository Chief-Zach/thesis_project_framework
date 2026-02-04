The LLM integration for this project is done through two files, an llm_service.py and llm_manager.py, both of which are found in `application/app/utils`.

### LLM Service
The LLM service file utilizes an abstract class to create connectors to various LLM APIs to make the setup process extremely simple. For each of the classes, they have a single public function, get_hint with identical signatures. This function takes the prompt which is constructed from the llm_prompt.txt file, as well as the solution to the level defined in the solutions folder. It also takes the past requests that the user made as a list of strings. From here each function performs the actions required to get a text response from the model and forward it back to the Page class so it can be returned to the user for a hint. 

### LLM Manager
To avoid any kind of messy setup functions, the LLM manager file contains two functions, get_llm and _create_llm. The create LLM function contains all of the code required to determine which LLM the developer has set in the config, as well as set up that LLM. This function has an LRU cache with a max size of 1 so that when the get_llm function is called, it will only run the function body on first call. This way, the same instance of a class can be used for all LLM calls since all of the get_hint functions are async. 

### Contributing New Models
If you would like to contribute other models to the service, or just fork for your own use, the process would be as follows:
#### Config and .env
Create a variable for your new LLM key in the .env file, and change the LLM variable in config.py to your own.
#### Create a new class in llm_service.py
This class should extend the LLMConnector and should follow a similar signature to the other classes. Set up the self.client using the library of your choice, just ensure that it supports async, or set up your own thread-locking similar to the Ollama class. If you need to add any helper functions to the class, please make them private (preceded with the _). Than you can create your get_hint function from the abstract method in LLMConnector. This should implement whatever API calls are necessary to get the response from your connected LLM.
```py
class MyNewConnector(LLMConnector):
    def __init__(self):
        super().__init__()
        self.client = MyAsyncLLM(
            api_key=os.getenv("MY_NEW_LLM_KEY"),
        )

    async def get_hint(self, prompt, past_queries: Union[List[str], None]=None):
        input_data = [{"role": "system", "content": prompt}]
        if past_queries is not None:
            for query in past_queries:
                input_data.append({"role": "user", "content": query})

        response = await self.client.chat(
            input = input_data
        )
        text = response.text

        return text

```

#### Edit llm_manager.py
Change the _create_llm function to include an elif statement for the name of your LLM, or at least what you have decided to call it in the config. For example:
```
    elif llm_type == "mynewllm":
        return MyNewConnector()
```


Now when you call get_llm anywhere in your project, your class will be used to get a hint.