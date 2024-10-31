source ./functions/venv/bin/activate
cd frontend
deno run build
cd ..
cd functions
pip install -r requirements.txt
cd ..
firebase deploy