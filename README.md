# faust_445
faust ticket#445 (functionning?)

Trying to reproduce https://github.com/robinhood/faust/issues/445

error traces in log file

# 1: kafka is running locally

# 2: Terminal: start worker
cd faust-master/examples
pipenv run faust -A tableofset worker 2>&1 |tee tableofset.log

