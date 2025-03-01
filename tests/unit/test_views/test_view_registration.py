### registration_buy page ###

def test_move_registration_buy_page(client):
    response = client.get('/move_registration_buy_page')
    assert response.status_code == 200


def test_input_buy(client):
    response = client.get('/input_buy')
    assert response.status_code == 200

### registration_income page ###

def test_move_registration_income_page(client):
    response = client.get('/move_registration_income_page')
    assert response.status_code == 200


def test_input_income(client):
    response = client.get('/input_income')
    assert response.status_code == 200


### registration_saving page ###

def test_move_registration_saving_page(client):
    response = client.get('/move_registration_saving_page')
    assert response.status_code == 200


def test_input_saving(client):
    response = client.get('/input_saving')
    assert response.status_code == 200


