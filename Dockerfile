FROM python:3.9-slim
COPY dist/ /tmp

RUN pip install --no-cache-dir -U pip && \
  pip install --no-cache-dir azure-cli && \
  pip install --no-cache-dir /tmp/azure_keyvault_browser*.whl && \
  rm /tmp/azure_keyvault_browser*.whl

CMD [ "kv" ]