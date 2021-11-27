# Backend

## Prerequisitos

Para una mejor organizacion se recomienda crear un virtual environment con el comando:

```bash
python3 -m venv venv
```

Luego corremos el virtual environment con:

```bash
source venv/bin/activate
```

Ahora necesitamos instalar todas las librerias que usa la aplicación usando el comando:

```bash
pip3 install -r requirements.txt
```

## Uso

Para correr el servidor usar el comando:

```bash
python main.py
```

Para correr los tests:

```bash
pytest tests
```

## Dockerfile

> :exclamation: Antes de seguir estos pasos se debe asegurar de tener instalado [`docker`](https://docs.docker.com/get-docker/).

Para construir la imagen

```bash
docker image build -t [nombre a dar a la imagen] .
```

Para correr el contenedor

```bash
docker container run --name [nombre a dar al contender] --env PORT=[numero de puerto] -p [puerto dado]:[puerto dado] [nombre de la imagen]
```
