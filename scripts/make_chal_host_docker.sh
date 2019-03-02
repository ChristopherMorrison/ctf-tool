docker image pull ubuntu
docker run -dit ubuntu
id=$(docker ps -a --format {{.ID}} | head -n 1)
docker exec -it $id /bin/bash

