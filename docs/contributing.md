# Contributing to the Nautobot Grafana Plugin

Pull requests are welcomed and automatically built and tested against multiple version of Python and multiple 
version of Nautobot through TravisCI.

The project is packaged with a light development environment based on `docker-compose` to help with the local 
development of the project and to run the tests within TravisCI.

The project is following Network to Code software development guidelines and is leveraging:
- Black, Pylint, Bandit and pydocstyle for Python linting and formatting.
- Django unit test to ensure the plugin is working properly.

## Development Environment

The project comes with a CLI helper based on [invoke](http://www.pyinvoke.org/) to help setup the development environment. 
The commands are listed below in 3 categories `dev environment`, `utility` and `testing`.

The development environment can be used in 2 ways. First, with a local poetry environment if you wish to develop outside 
of Docker. Second, inside of a docker container.

Note that for a functional development environment, you will need to follow the steps to link your chat client to your development environment.
Please see the instructions from the Nautbot ChatOps plugin
[`chat_setup.md`](https://github.com/nautobot/nautobot-plugin-chatops/blob/develop/docs/chat_setup/chat_setup.md) as well
as enabling the `/grafana` slash command to your specific chat client as noted in this [`installation.md`](installation.md).


For the development environment, these parameters are specified by copying the
provided `creds.env.example` file to `creds.env` and customizing the contents of the copied file appropriately.

#### Invoke tasks

The [PyInvoke](http://www.pyinvoke.org/) library is used to provide some helper commands based on the environment.  There are a few configuration parameters which can be passed to PyInvoke to override the default configuration:

* `nautobot_ver`: the version of Nautobot to use as a base for any built docker containers (default: 1.0.2)
* `project_name`: the default docker compose project name (default: nautobot_plugin_chatops_grafana)
* `python_ver`: the version of Python to use as a base for any built docker containers (default: 3.6)
* `local`: a boolean flag indicating if invoke tasks should be run on the host or inside the docker containers (default: False, commands will be run in docker containers)
* `compose_dir`: the full path to a directory containing the project compose files
* `compose_files`: a list of compose files applied in order (see [Multiple Compose files](https://docs.docker.com/compose/extends/#multiple-compose-files) for more information)

Using PyInvoke these configuration options can be overridden using [several methods](http://docs.pyinvoke.org/en/stable/concepts/configuration.html).  Perhaps the simplest is simply setting an environment variable `INVOKE_NAUTOBOT_PLUGIN_CHATOPS_GRAFANA_VARIABLE_NAME` where `VARIABLE_NAME` is the variable you are trying to override.  The only exception is `compose_files`, because it is a list it must be overridden in a yaml file.  There is an example `invoke.yml` in this directory which can be used as a starting point.

#### Local Poetry Development Environment

1. Copy `development/creds.example.env` to `development/creds.env` (This file will be ignored by git and docker)
2. Uncomment the `POSTGRES_HOST`, `REDIS_HOST`, and `NAUTOBOT_ROOT` variables in `development/creds.env`
3. Create an invoke.yml with the following contents at the root of the repo:

```shell
---
nautobot_plugin_chatops_grafana:
  local: true
  compose_files:
    - "docker-compose.requirements.yml"
```

3. Run the following commands:

```shell
poetry shell
poetry install --extras nautobot
export $(cat development/dev.env | xargs)
export $(cat development/creds.env | xargs) 
invoke start && sleep 5
nautobot-server migrate
```

> If you want to develop on the latest develop branch of Nautobot, run the following command: ``poetry add git+https://github.com/nautobot/nautobot@develop``. After the ``@`` symbol must match either a branch or a tag.

4. You can now run nautobot-server commands as you would from the [Nautobot documentation](https://nautobot.readthedocs.io/en/latest/) for example to start the development server:

```shell
nautobot-server runserver 0.0.0.0:8080 --insecure
```

Nautobot server can now be accessed at [http://localhost:8080](http://localhost:8080).

#### Docker Development Environment

This project is managed by [Python Poetry](https://python-poetry.org/) and has a few requirements to setup your development environment:

1. Install Poetry, see the [Poetry Documentation](https://python-poetry.org/docs/#installation) for your operating system.
2. Install Docker, see the [Docker documentation](https://docs.docker.com/get-docker/) for your operating system.

Once you have Poetry and Docker installed you can run the following commands to install all other development dependencies in an isolated python virtual environment:

```shell
poetry shell
poetry install
invoke db-import
invoke start
```

Nautobot server can now be accessed at [http://localhost:8080](http://localhost:8080).
Plugin Documentation can now be accessed at [http://localhost:8001](http://localhost:8001).
Mattermost server can now be accessed at [http://localhost:8002](http://localhost:8002) with the username `admin` and the password `password`.
Grafana can now be accessed at [http://localhost:3000](http://localhost:3000) with the username `admin` no password.
Prometheus can now be accessed at [http://localhost:9090](http://localhost:9090).

### CLI Helper Commands

The project is coming with a CLI helper based on [invoke](http://www.pyinvoke.org/) to help setup the development environment. The commands are listed below in 3 categories `dev environment`, `utility` and `testing`.

Each command can be executed with `invoke <command>`. Environment variables `INVOKE_NAUTOBOT_PLUGIN_CHATOPS_GRAFANA_PYTHON_VER` and `INVOKE_NAUTOBOT_CHATOPS_EXTENSION_GRAFANA_NAUTOBOT_VER` may be specified to override the default versions. Each command also has its own help `invoke <command> --help`

#### Docker dev environment

```no-highlight
  build            Build all docker images.
  debug            Start Nautobot and its dependencies in debug mode.
  destroy          Destroy all containers and volumes.
  restart          Restart Nautobot and its dependencies.
  start            Start Nautobot and its dependencies in detached mode.
  stop             Stop Nautobot and its dependencies.
```

#### Utility

```no-highlight
  cli              Launch a bash shell inside the running Nautobot container.
  create-user      Create a new user in django (default: admin), will prompt for password.
  makemigrations   Run Make Migration in Django.
  nbshell          Launch a nbshell session.
```

#### Testing

```no-highlight
  bandit           Run bandit to validate basic static code security analysis.
  black            Run black to check that Python files adhere to its style standards.
  flake8           This will run flake8 for the specified name and Python version.
  pydocstyle       Run pydocstyle to validate docstring formatting adheres to NTC defined standards.
  pylint           Run pylint code analysis.
  tests            Run all tests for this plugin.
  unittest         Run Django unit tests for the plugin.
```


