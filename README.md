# faust_445
faust ticket#445 (functionning?)
rror traces in log file

# 1: kafka is running locally

# 2: Terminal: start worker
cd faust-master
pipenv run faust -A tableofset worker 2>&1 |tee tableofset.log

"""
Also tried without specifying "worker" and got 
hadoop@pascal-asus:~/kafka_2.11-2.3.0/faust-master$ pipenv run faust -A examples.tableofset 2>&1 |tee tableofset.log
Usage: faust [OPTIONS] COMMAND [ARGS]...
Try "faust --help" for help.

Error: Missing command.
sys:1: RuntimeWarning: coroutine 'StampedeWrapper.__call__' was never awaited

"""

