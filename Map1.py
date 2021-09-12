from StateTA import *

class Map(IContext):

  TYPE  = 'type'
  VAR   = 'var'
  NUM   = 'num'
  ASIGN = 'asign'
  OTHER = 'other'
  END   = 'end'

  last_name = None
  __nums = '0123456789'
  __leters = 'asdfghjklqwertyuiopzxcvbnm'
  __reserved_types = {'int', 'long', 'short'}
  __special_types = {'='}

  def __init__(self, states: StateList=[], *args, **kwargs):
    super().__init__(states, *args, **kwargs)

  def createMap(self):
    errorNode = ErrorState()
    errorNode.transition_default = errorNode
    startNode   = NormalState(errorNode, context_=self)
    preTypeNode = NormalState(errorNode, context_=self)
    typeNode    = NormalState(errorNode, context_=self)
    nameNode    = NormalState(errorNode, context_=self)
    asignNode   = NormalState(errorNode, context_=self)
    varNumNode  = NormalState(errorNode, context_=self)
    varNameNode = NormalState(errorNode, context_=self)
    finNode     = NormalState(errorNode, context_=self)

    self._states = [
      preTypeNode,
      typeNode,
      nameNode,
      asignNode,
      varNumNode,
      varNameNode,
      finNode,
      errorNode
    ]

    self._final_state = finNode
    self._start_state = startNode

    def startGoFunc(context: IContext, token: Token) -> TransitionResult:
      return token[1]

    def nameGoFunc(context: IContext, token: Token) -> TransitionResult:
      context.last_name = token[1]
      return token[1]

    def varNameGoFunc(context: IContext, token: Token) -> TransitionResult:
      context._token_storage[context.last_name] = token[1]
      return token[1]

    def varNumGoFunc(context: IContext, token: Token) -> TransitionResult:
      context._token_storage[context.last_name] = int(token[1])
      return token[1]

    startNode.addTransition   (self.NUM,   preTypeNode,   startGoFunc)
    preTypeNode.addTransition (self.TYPE,  typeNode)
    preTypeNode.addTransition (self.VAR,   nameNode,      nameGoFunc)
    typeNode.addTransition    (self.VAR,   nameNode,      nameGoFunc)
    nameNode.addTransition    (self.ASIGN, asignNode)
    nameNode.addTransition    (self.END,   finNode)
    asignNode.addTransition   (self.NUM,   varNumNode,    varNumGoFunc)
    asignNode.addTransition   (self.VAR,   varNameNode,   varNameGoFunc)
    varNameNode.addTransition (self.END,   finNode)
    varNumNode.addTransition  (self.END,   finNode)


  def check_type(self, token: str) -> Key:
    token = token[:-1] if token[-1] == '\n' else token
    if token in self.__reserved_types:
      return self.TYPE
    elif token in self.__special_types:
      return self.ASIGN
    elif 0 < len(token) <= 16:
      isVar = False
      isNum = False
      token = token.lower()
      if token[0] in self.__nums:
        isNum = True
      if token[0] in self.__leters:
        isVar = True
      for i in token[1:]:
        if isNum and i not in self.__nums:
          return self.OTHER
        if isVar and not (i in self.__nums or i in self.__leters):
          return self.OTHER
      if isNum:
        return self.NUM
      elif isVar:
        return self.VAR
    return self.OTHER

  def logFormat(self, status: Status, tokens: TokenList):
    if status is Status.OK_STATUS:
      return f"<{status.name}> {tokens[0]} - {tokens[1]}"
    return f"<{status.name}> {tokens}"

  def pre_run(self, pattern: str, *args, **kwargs) -> TokenList:
    super().pre_run(pattern, *args, **kwargs)
    raws = pattern.split()
    tokens: TokenList = list()
    for raw in raws:
      t = self.check_type(raw)
      if t == self.OTHER:
        return Status.NAME_ERROR, tokens
      tokens.append((t, raw))
    tokens.append((self.END, None))
    return Status.OK_STATUS, tokens

  def runFromFile(self, filename: str, logger: str="log.log", *args, **kwargs):
    with open(filename, mode='r', *args, **kwargs) as inp:
      with open(logger, encoding='utf-8', mode='w+') as log:
        for num, line in enumerate(inp.readlines()):
          s = f"{num} {line}"
          status, res = self.run(s)
          log_s = self.logFormat(status, res)+'\n'
          log.write(log_s)
    
  def runFromConsole(self, *args, **kwargs):
    try:
      num = 1
      while True:
        inp = input()
        s = f"{num} {inp}"
        status, res = self.run(s)
        print(self.logFormat(status, res))
        num += 1
    except KeyboardInterrupt:
      pass
    except EOFError:
      pass
    finally:
      print()


class NormalState(IState):
  pass


class ErrorState(IState):
  pass


def loop_input(msg, vals):
  print(msg, end='')
  key = input()
  while key not in vals:
    print('Incorrect input. Try again')
    print(msg, end='')
    key = input()
  return key

if __name__ == '__main__':
  DEBUG = True

  map = Map()
  map.createMap()
  import sys
  args = len(sys.argv)
  if args == 1:
    print('Press Ctrl+d to exit')
    map.runFromConsole()
  elif args == 2:
    map.runFromFile(sys.argv[1])
  elif args == 3:
    map.runFromFile(sys.argv[1], sys.argv[2])
  
  if DEBUG:
    print(f"token_storage: {map.token_storage}")
  