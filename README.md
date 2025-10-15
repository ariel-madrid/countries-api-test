## Instrucciones para Ejecucion

El test se encuentra Dockerizado por lo que se requiere de tener Docker instalado previamente, dejo el paso a paso para su instalación (Ubuntu) en el siguiente link:

  1. https://docs.docker.com/engine/install/ubuntu/

Luego de haber instalado docker, en la carpeta raiz del proyecto, para construir y correr en segundo plano, ejecutar:

  * docker compose up --build -d 

En caso de no tener Docker instalado seguir las siguientes instrucciones:

  * Instalar requierments: pip install -r requirements.txt
  * Ejecutar aplicacion (dentro de la carpeta "app"): uvicorn main:app --host 0.0.0.0 --port 8000
