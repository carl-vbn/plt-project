docker build -t code-generation .
docker run -it --rm \
    -v .:/app \
    code-generation:latest $*