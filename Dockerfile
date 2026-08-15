FROM python:3.12-slim

WORKDIR /app

# install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# copy dependencies
COPY pyproject.toml uv.lock ./

# install dependencies form uv.lock - dont generate new
RUN uv sync --frozen --no-install-project --no-dev

ENV PLAYWRIGHT_BROWSERS_PATH=/ms-playwright

# install playwright
RUN .venv/bin/python -m playwright install --with-deps

# copy source code
COPY src ./
COPY tests ./
COPY scrapper.py ./
COPY urls.txt ./

# make non-root user and assign that to a group
RUN groupadd --system appgroup && \
    useradd --system --gid appgroup --create-home appuser && \
    chown -R appuser:appgroup /app && \
    chmod -R 755 /ms-playwright

# switch to non-root user to start the app
USER appuser

CMD ["/app/.venv/bin/python", "scrapper.py"]
