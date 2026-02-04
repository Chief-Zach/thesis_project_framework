## Docker
A Dockerfile has been provided for you to simply deploy, both for production and for debug, in a containerized environment. The Dockerfile will by default set the environment variable "DEBUG" to 1, meaning true, so it will by default run the application with Uvicorn instead of Gunicorn, and will run with the development version of the config. You can change this environment variable with the commands shown below. 

To build the Docker container, you can run:

```
docker build -t {container_name} .
```

Internally, the Docker container will run the application on port 8000. You can forward this port to whatever port on the local machine that you would like, but in the demos below, it is forwarded to local port 8000. The internal Docker port can be changed by altering the start_server.sh script, and altering the bind and port fields.

For running in debug mode, you can run:

```
docker run -p 8000:8000 -e DEBUG=1 {container_name}
```
or
```
docker run -p 8000:8000 {container_name}
```

Since the default debug is set to true.

For running in production mode, or just your debug=False mode, you can set the debug flag to 1 when running the container:

`
docker run -p 8000:8000 -e DEBUG=0 {container_name}
`
## Local
The same file that Docker uses to deploy in the Docker container can be used to deploy locally as well. One extra step that must be completed is the installation of the Python packages required to run the application. This can be done by navigating into the application directory and running:
```
pip install -r requirements.txt
```
It is recommended to do this in a virtual environment. After installing the Python packages, you can run the shell script that will start the application. If you would like to run in production mode, you can set the DEBUG environment variable to 0. However, it is recommended to set the bind address to a Unix socket if deploying to the internet through a reverse proxy such as NGINX, and the start_server.sh is mainly meant to be used by Docker. 
