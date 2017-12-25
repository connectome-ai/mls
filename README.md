# Server and client for hosting ML based solutions

## Installation

`pip3 install myLittleServer`

## Server creation

Server can implement simple interface with just predict method. Use it, when you don't need to save any information which can be obtained in progress.

Example of class which fits expected interface:

```python
class Interface:

  def __init__(self, **kwargs):
    pass

  # data can be any object, which you expect to receive
  def predict(self, data):
    return data
```

To run server with such interface, type this code:
```python
from mls import Server
# Create instance of Interface class
interface = Interface()
# Server initialization
server = Server(port=3001, ml=interface)
```

If predict is not a pure function (results of it depends on the state), than StateMachine is your way to go!
Example of class which fits expected interface:

```python
class StateMachineInterface:

   # data can be any object, which you expect to receive
   # method has to return events in predefined format
   def update(self, data):
     events = self._process(data)
     return events

   # data can be any object, which you expect to receive
   def set_state(self, state):
     self._update_my_state(state)
     return None
```

To run server with such interface, type this code:

```python
interface = StateMachineInterface()

from mls import StateMachine

# Server initialization
server = StateMachine(port=3001, ml=interface)
```

Following syntax is the same for both `Server` and `StateMachine`.

You can start ml module initialization process inside server. It can be helpful if you want to check when server is ready. In that case pass Interface constructor and it's kwargs as separate params.

```python
from mls import Server
# Your init kwargs
config = {'foo': 'bar'}
# Server initialization
# You need to provide class itself, not object of that class
# It's the same as if you do Interface(**ml_config)
server = Server(port=3001, ml=Interface, ml_config=config)
```

You can turn off server logs by providing `log=False`:
```python
# You can turn off logging
server = Server(port=3001, ml=interface, log=False)
```

## Client creation

Client initialization:
```python  
from mls import Client

# Client initialization
client = Client(address='http://localhost:3001')
```

Check server status:
```python
# Check that server launched
is_started = client.started()
# Check that ml module is set up and ready for work
is_ready = client.ready()
# You can call only ready() as it has inner check for case, when server hasn't started
```

Result of client call is [future](https://docs.python.org/3/library/concurrent.futures.html). So all it's methods work fine.

```python
res = client.predict(data_to_process)
```

Get the body of the result. It's a blocking operation:

```python
data = res.result()
```

Best practice is to check res for exception before running `result()` method as it will throw exception if one occurred on the server side.

```python
# Otherwise res.result() will raise an exception.
if res.exception() is None:
  data = res.result()
```

You can check if call to server is finished:

```python
while True:
  if not res.done():
    sleep(1)
  else:
    do_stuff(res.result())
```

You can also add a callback function:

```python
res.add_done_callback(lambda res: do_stuff(res.result()))
```
