from abc import ABC, abstractmethod
from os import name, stat
import typing
import enum

class IState(ABC):pass
class IContext(ABC):pass
class Transition:pass

# TYPES
StateList = typing.List[IState]
Key = typing.Union[str, int]
Token = typing.Tuple[Key, typing.Any]
TokenList = typing.List[Token]
TokenDict = typing.Dict[Key, Token]
TransitionResult = typing.Tuple[typing.Union[Token, None], IState]
TransitionCallback = typing.Callable[[IContext, Token], TransitionResult]
TransitionDict = typing.Dict[Key, Transition]

class Status(enum.Enum):
  OK_STATUS = 0
  BAD_STATUS = 1
  NAME_ERROR = 2



class IState(ABC):

  _transition_dict: TransitionDict
  _transition_default: Transition
  _context: IContext = None
  
  def __init__(self, defaultTarget: IState=None, defaultGoFunc: TransitionCallback=None, context_:IContext=None):
    self._transition_default = Transition(defaultTarget, self, defaultGoFunc)
    self._transition_dict = dict()
    self._context = context_

  def __getitem__(self, key: Key):
    if key not in self._transition_dict.keys():
      return self.transition_default
    return self._transition_dict[key]

  @property
  def context(self):
    return self._context

  @property
  def transition_default(self):
    return self._transition_default

  @transition_default.setter
  def transition_default(self, transition: Transition):
    self._transition_default = transition

  @transition_default.setter
  def transition_default(self, target: IState):
    self._transition_default.setTarget(target)

  def setTransitionDefault(self, defaultTarget: IState=None, defaultGoFunc: TransitionCallback=None):
    self._transition_default = Transition(defaultTarget, self, defaultGoFunc)

  def addTransition(self, key: Key, target: IState, goFunc: TransitionCallback=None):
    self._transition_dict[key] = Transition(target, self, goFunc)

  def remTransition(self, key: Key) -> bool:
    """Should I use it?"""
    if key in self._transition_dict.keys():
      if self._transition_dict[key] is self._transition_default:
        self._transition_default = None
      self._transition_dict.pop(key)
      return True
    return False


class IContext(ABC):

  _token_storage: TokenDict
  _states: StateList
  _final_state: IState = None
  _start_state: IState = None

  def __init__(self, states: StateList, *args, **kwargs):
    self._states = states
    if 'final' in kwargs.keys() and issubclass(type(kwargs['final']), IState):
      self._final_state = kwargs['final']
    if 'start' in kwargs.keys() and issubclass(type(kwargs['start']), IState):
      self._start_state = kwargs['start']
    self._token_storage = dict()

  @property
  def final_state(self):
    return self._final_state

  @property
  def start_state(self):
    return self._start_state
  
  @property
  def states(self):
    return self.states

  @property
  def token_storage(self):
    return self._token_storage
  
  @final_state.setter
  def final_state(self, state: IState):
    self._final_state = state

  @start_state.setter
  def start_state(self, state: IState):
    self.start_state = state

  @abstractmethod
  def pre_run(self, pattern, *args, **kwargs) -> typing.Tuple[Status, TokenList]:
    pass

  def run(self, pattern) -> typing.Tuple[Status, TokenList]:
    status, tokens = self.pre_run(pattern)
    if status is not Status.OK_STATUS:
      return (status, [])
    else:
      curState: IState = self.start_state
      result = []
      print(*tokens, sep=' -> ')
      for token in tokens:
        out, curState = curState[token[0]](token)
        if out is not None:
          result.append(out)
      resStatus = Status.OK_STATUS if curState == self._final_state else Status.BAD_STATUS
      return (resStatus, result)


class Transition:

  target: IState
  from_: IState
  goFunc: TransitionCallback

  def __init__(self, target, from_:IState=None, goFunc:TransitionCallback=None):
    self.target = target
    self.from_ = from_
    self.goFunc = goFunc

  def __call__(self, token:Token, *args, **kwargs) -> TransitionResult:
    res = None
    if self.goFunc is not None:
      res = self.goFunc(self.from_.context, token)
    return res, self.target

  def setTarget(self, target: IState):
    self.target = target

  def __str__(self) -> str:
    return f"<Transtition> {self.from_} -> {self.target} : {self.goFunc}"

  def __repr__(self) -> str:
    return self.__str__()

if __name__ == '__main__':
  pass