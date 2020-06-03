# Быстрый локальный старт

Требуется предварительная установка

* python
* virtualenv
* прописать в hosts  --  127.0.0.1 kafka

```bash
rm -rf env || true
virtualenv --python=python3.8 env
source env/bin/activate
make sync-requirements
make run-deps
make run-server
```
# sms_gateway
