import pytest

from app import create_app

from app.models.database import Database
# @pytest.fixture
@pytest.fixture(scope='module')
def test_client():
    """Tells Flask that app is in test mode
    """

    app = create_app('TESTING')
    db = Database()
    db.empty_tables()
    db.cursor.execute(open("test_data.sql", "r").read())

    test_client = app.test_client()

    context = app.app_context()
    context.push()


    yield test_client

    context.pop()

#
#
# @pytest.fixture(scope='function')
# def init_database():
#     # Create the database and the database table
#     db = Database()
#     db.empty_tables()
#
#     # Insert user data
#
#     # db.session.commit()
#
#     yield db  # this is where the testing happens!
#
#     db.drop_all()