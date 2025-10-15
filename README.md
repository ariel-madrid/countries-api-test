## Instrucciones para Ejecucion

El test se encuentra Dockerizado por lo que se requiere de tener Docker instalado previamente, dejo el paso a paso para su instalación (Ubuntu):

  1.sudo apt-get update
  2-sudo apt-get install ca-certificates curl
  3.sudo install -m 0755 -d /etc/apt/keyrings
  4.sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
  5.sudo chmod a+r /etc/apt/keyrings/docker.asc
  6.echo \
    "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu \
    $(. /etc/os-release && echo "${UBUNTU_CODENAME:-$VERSION_CODENAME}") stable" | \
    sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
  7.sudo apt-get update
  8.sudo apt-get install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin


Luego de haber instalado docker en la carpeta raiz del proyecto para construir y correr en segundo plano, ejecutar:

docker compose up --build -d 
