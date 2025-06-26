# Context Window Prime

RUN:
make install
source .venv/bin/activate
make format
make lint
make test

READ:
ai_context/IMPLEMENTATION_PHILOSOPHY.md
ai_context/MODULAR_DESIGN_PHILOSOPHY.md
