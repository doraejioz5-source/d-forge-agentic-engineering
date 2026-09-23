#!/bin/bash
cd "$(dirname "$0")"

if [ ! -d ".venv" ]; then
  python3 -m venv .venv
fi

source .venv/bin/activate
pip install -r requirements.txt

if [ ! -f ".env" ]; then
  cp .env.example .env
  echo ""
  echo "먼저 .env 파일에 OPENAI_API_KEY를 입력해주세요."
  open -e .env
  exit 0
fi

streamlit run app.py
