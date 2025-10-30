# Nadhi: The Backend

This section of the app is the part that connects all components. It's a FastAPI server, an
asynchronous server built with Python. This allows operations, like saving an image to storage, or
writing a new item to the database, to be done while also processing other people's requests.

Each section of the backend has its own subfolder. Routes to each subsection can be found in /router.py.
These each are imported by main.py and set up by the primary FastAPI app. This app uses SQLAlchemy for
Object-relational-mapping (ORM) support, so adding data to the database is very simple. The schema for each
subsection are in /schemas.py, and are then imported by /database.py to create the database and run the app.

To run this app, you should run `pip install -r requirements.txt` and then use the `fastapi run` utility
provided by the FastAPI package for testing. You can test each individual endpoint by going to the
`/docs` endpoint in a web browser.

### P.S. Nadhi, translated from Tamil, means: "river". It's also the acronym
