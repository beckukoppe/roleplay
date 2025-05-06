rm -rf ./log

if [ ! -d "venv" ]; then
  echo "Creating virtual environment..."
  python -m venv venv
fi

if [ -z "$VIRTUAL_ENV" ]; then
  echo "Activating virtual environment..."
  source venv/bin/activate
  pip install -r requirements.txt
fi


python source/main.py
