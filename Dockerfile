# build me with `docker build -t cyberatuc/ctf-tool .` from the root of the repo (respects branch)
FROM debian:10

# Copy tool folder
COPY . /ctf-tool/
WORKDIR /ctf-tool/

# Install deps
RUN scripts/install_required_packages.sh &&\
    pip3 install -r requirements.txt

# nothing fancy this time
CMD ["bash"]

