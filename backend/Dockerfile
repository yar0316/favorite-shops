FROM public.ecr.aws/lambda/python:3.13

# Install dependencies using uv (if needed) or pip
COPY pyproject.toml .
RUN pip install uv && uv pip install --system -r pyproject.toml

# Copy source code and layers
COPY layers/ /var/task/layers/
COPY functions/ /var/task/functions/

# Set PYTHONPATH to include layers
ENV PYTHONPATH="/var/task:/var/task/layers:${PYTHONPATH}"

# CMD is set per service in docker-compose
