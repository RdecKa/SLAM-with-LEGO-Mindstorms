from typing import Callable


class Action():
    def __init__(self, f: Callable, *args, **kwargs):
        self.f = f
        self.args = args
        self.kwargs = kwargs

    def execute(self, *args, **kwargs):
        self.f(*args, *self.args, **kwargs, **self.kwargs)

    def update_args(self, *args, **kwargs):
        self.args = (*self.args, *args)
        self.kwargs = {**self.kwargs, **kwargs}


class ActionWithParams():
    def __init__(self, action: Action, *args, **kwargs):
        self.action = action
        self.args = args
        self.kwargs = kwargs

    def execute(self):
        self.action.execute(*self.args, **self.kwargs)
