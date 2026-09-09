1.
pip install fastapi uvicorn pydantic pytest httpx
Run the FastAPI development server:

2.
uvicorn main:app --reload
Run the automated tests:

3.
pytest test_main.py -v