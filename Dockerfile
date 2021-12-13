FROM python:3.9-slim

ENV AZURE_KEYVAULT_BROWSER_CONFIG /app/.azure-keyvault-browser.toml

WORKDIR /app

COPY dist/ /tmp/
RUN pip install --no-cache-dir /tmp/azure_keyvault_browser*.whl

ENTRYPOINT ["kv"]