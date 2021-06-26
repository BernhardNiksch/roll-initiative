# Roll Initiative

`Roll Initiative` is (or, at least, attempts to be) a data-driven campaign and character manager 
for D&D, built using [Django](https://www.djangoproject.com/) and 
[Django Rest Framework](https://www.django-rest-framework.org/).

---

## Getting Started

Assuming you already have [PostgreSQL](https://www.postgresql.org/) installed, all necessary
users created, and requirements installed; Create the DB tables by applying the migrations.

    python manage.py migrate

Load the fixtures into the database. (The fixtures provided merely resemble real D&D data)

    python manage.py loaddata 
        character/fixtures/character.json \
        equipment/fixtures/equipment.json \
        features/fixtures/features.json \
        monster/fixtures/monster.json \
        campaign/fixtures/campaign.json

Get the server running.

    python manage.py runserver

Navigate to `http://127.0.0.1:8000/swagger-ui/` in your browser to visualise and interact
with the API's resources.

The model schema can be viewed at `http://127.0.0.1:8000/schema-graph/` and 
`http://127.0.0.1:8000/schema-plate/`, the former displaying the model class relationships,
and the latter an entity relationship diagram (ERD). Having both feels like overkill, but
they serve somewhat different purposes.
