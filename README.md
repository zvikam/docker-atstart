# Introduction

This script will monitor the docker service for new containers being started.<br />
When a new container is started, a specified file (or directory) will be copied into it and (optionally) a command will be executed inside the container.<br />

## Blog

The code is part of a blog post which is available here: 

    http://www.correlsense.com/automating-docker-container-monitoring/

## Usage

    docker-atstart.py [-h] [--container CONTAINER] --source SOURCE --dest DEST ...

positional arguments:

    command                 command to run after injection

optional arguments:

    -h, --help              show help message and exit
    --container CONTAINER   container(s) to inject (wildcards accepted)
    --source SOURCE         file/directory to inject
    --dest DEST             path inside container where the injected files will be placed

## Examples

Copy (and extract) a tar file from the host into the container
```bash
  python ./docker-atstart.py --source /tmp/data.tar --dest /tmp/data
```
Copy a directory from the host into the container
```bash
  python ./docker-atstart.py --source /tmp/data --dest /tmp/data
```
Copy a directory from the host into the container and run a command
```bash
  python ./docker-atstart.py --source /tmp/data --dest /tmp/data /tmp/data/process_data
```
Inject only into instances of our images
```bash
  python ./docker-atstart.py --source /tmp/data.tar --dest /tmp/data --container 'my-*'
```
# License

docker-atstart is licensed under the MIT License. See LICENSE for the full license text.
