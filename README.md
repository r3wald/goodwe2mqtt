# goodwe2mqtt

Collect data from Goodwe inverter and send them to mqtt broker.

## preparation

    git clone git@github.com:r3wald/goodwe2mqtt.git
    cd goodwe2mqtt
    cp .env.example .env
    vi .env
    
## install dependencies

    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt

## usage

    source venv/bin/activate
    python goodwe2mqtt.py

## usage with pm2

    source venv/bin/activate
    pm2 start app.py --interpreter=python3 --name=goodwe2mqtt
    pm2 save

## development

### create virtual environment

    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt

### create requirements.txt

    pip freeze > requirements.txt
