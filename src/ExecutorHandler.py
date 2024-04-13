"""
    The Executor class is an abstract class that defines the interface for the Executor classes.
    An Executor class is a class that, given the ASP output as input, executes the task 
    specified inside the `run` function (which must be implemented by the child class).
"""
from dataclasses import dataclass
from typeguard import typechecked
from TaskHandler import TaskHandler
from g4f import ChatCompletion, Provider

@typechecked
@dataclass(frozen=True)
class ExecutorHandler(TaskHandler):
    
    def run(self) -> None:
        raise NotImplementedError("The run method must be implemented by the child class.")