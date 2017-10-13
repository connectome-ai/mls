# Server and client for hosting ML based solutions

## Installation

`pip3 install git+https://github.com/connectome-ai/mls`

## Server creation

```python
  # Example of class which fits expected interface
  class Interface:

    # data can be any object, which you expect to receive
    def predict(self, data):
      return data

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

  interface = Interface()

  from mls import Server, StateMachine

  # Server initialization
  server = Server(port=3001, ml=interface)

  # Server with state support initialization
  server = StateMachine(port=3001, ml=sm_interface)

  # You can start ml module initialization process inside server
  # It can be helpful if you want to check if server is ready
  # You need to provide class itself, not object of that class
  # It's the same as if you do Interface(**ml_config)
  server = Server(port=3001, ml=Interface, ml_config={})

  # You can turn off logging
  server = Server(port=3001, ml=interface, log=False)

  # Launch server, it's a blocking operation
  server()
```

## Client creation

```python  
  from mls import Client

  # Client initialization
  client = Client(address='http://localhost:3001')

  # Check that ml module is set up and ready for work
  # If server is not launched at the moment of request it will raise an exception
  is_ready = client.ready()

  # Result of client call is [future](https://docs.python.org/3/library/concurrent.futures.html)
  res = client.predict(data_to_process)

  # Get the body of the result. It's a blocking operation.
  data = res.result()

  # Check that request succeeded.
  # Otherwise res.result() will raise an exception.
  if res.exception() is None:
    data = res.result()

  # You can check if call to server is finished.
  while True:
    if not res.done():
      sleep(1)
    else:
      do_stuff(res.result())

  # You can also add a callback function
  res.add_done_callback(lambda res: do_stuff(res.result()))
```
