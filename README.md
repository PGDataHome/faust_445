# faust_445
faust ticket#445 (functionning?)

Trying to reproduce https://github.com/robinhood/faust/issues/445

error traces in log file

# 1: kafka is running locally

# 2: Terminal: start worker
cd ~/kafka
pipenv install
pipenv run faust -A analytics worker 2>&1 |tee analytics.log

