# build from the root of the repo (respects branch) with: 
#   docker build -t cyberatuc/ctf-tool .` 

# run (using docker engine socket passthrough) with:
#   docker run -it -v /var/run/docker.sock:/var/run/docker.sock
FROM debian:10

# Copy tool folder
COPY . /ctf-tool/
WORKDIR /ctf-tool/

# Install deps
RUN scripts/install_required_packages.sh &&\
    pip3 install -r requirements.txt

# nothing fancy this time
CMD ["bash"]

