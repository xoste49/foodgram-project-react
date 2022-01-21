FROM python:3.10-slim
WORKDIR /app
RUN --mount=type=cache,target=/root/.cache/pip pip install --upgrade pip
RUN --mount=type=cache,target=/root/.cache/pip pip install --upgrade setuptools
COPY . .
RUN --mount=type=cache,target=/root/.cache/pip pip install -r requirements.txt
RUN python manage.py migrate
RUN python manage.py collectstatic --noinput
