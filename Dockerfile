FROM python:3.12
RUN pip intall poetry
COPY . /src
WORKDIR /src
RUN poetry install
EXPOSE 8501
ENTRYPOINT [ "poetry", 'run', 'stremlit', 'run', 'app.py', '--server.port=8501', 'server.address=0.0.0.0']
# ENTRYPOINT ["poetry","run", "python", "main.py"]
