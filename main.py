#import curses
#from curses import wrapper
import threading
from colorama import Fore

class CLIItem:
    def __init__(self, name,):
        self.name = name

    def use(self, position):
        return self.name

    def update(self, **kwargs):
        return True

class CLILoadingBar(CLIItem):
    def __init__(self, name, progress=0, **kwargs):
        super().__init__(name)
        self.progress = progress
        self.waiter = threading.Event()
        self.kwargs_handler(**kwargs)
        self.usages = []

    def kwargs_handler(self, **kwargs):
        if 'width' in kwargs and isinstance(kwargs['width'], int):
            self.width = kwargs['width']
        else:
            self.width = 20
        if 'start_char' in kwargs and isinstance(kwargs['start_char'], str):
            self.start_char = kwargs['start_char']
        else:
            self.start_char = '#'
        if 'end_char' in kwargs and isinstance(kwargs['end_char'], str):
            self.end_char = kwargs['end_char']
        else:
            self.end_char = '#'
        if 'empty_char' in kwargs and isinstance(kwargs['empty_char'], str) and len(kwargs['empty_char']) == 1:
            self.empty_char = kwargs['empty_char']
        else:
            self.empty_char = '-'
        if 'full_char' in kwargs and isinstance(kwargs['full_char'], str) and len(kwargs['full_char']) == 1:
            self.full_char = kwargs['full_char']
        else:
            self.full_char = '='
        if 'prefix' in kwargs and isinstance(kwargs['prefix'], str):
            self.prefix = kwargs['prefix']
        else:
            self.prefix = ''
        if 'suffix' in kwargs and isinstance(kwargs['suffix'], str):
            self.suffix = kwargs['suffix']
        else:
            self.suffix = ''
        if 'done' in kwargs and isinstance(kwargs['done'], str):
            self.done = kwargs['done']
        else:
            self.done = None
        if 'format' in kwargs:
            if 'format' in kwargs['format'] and 'items' in kwargs['format']:
                if isinstance(kwargs['format']['items'], list) and isinstance(kwargs['format']['format'], str):
                    inserts = []
                    opened = None
                    slashed = False
                    processed = -1
                    # Process the format string to find all {}
                    for i, cha in enumerate(kwargs['format']['format']):
                        if opened is not None:
                            if cha == '}':
                                inserts.append(i - 1)
                                opened = None
                        else:
                            raise ValueError(f"Invalid format string: {kwargs['format']['format'][:processed]}{Fore.YELLOW + cha + Fore.RED}{kwargs['format']['format'][i+1:]}\nExpected '}}', instead got: {cha}")
                        if not slashed:
                            if cha == '{':
                                opened = i
                            if cha == '\\':
                                slashed = True
                        else:
                            processed = i
                    # Process the items to validate them
                    if len(inserts) != len(kwargs['format']['items']):
                        raise ValueError(f"Number of format items ({len(kwargs['format']['items'])}) does not match number of inserts ({len(inserts)}) in format string: {kwargs['format']['format']}")
                    for item in kwargs['format']['items']:
                        if not isinstance(item, (str, CLIItem)):
                            raise ValueError(f"Format item must be a string or CLIItem, got: {type(item)}")
                        if isinstance(item, str):
                            if item not in ['name', 'progress', 'bar']:
                                raise ValueError(f"Invalid format item string: {item}. Must be 'name' or 'progress'.")
                    self.format_string = kwargs['format']['format']
                    self.format_items = kwargs['format']['items']
        if not hasattr(self, 'format_string'):
            self.format_string = '{}: {} {}%'
            self.format_items = ['name', 'bar', 'progress']
            self.inserts = [0, 4, 7]

    def update(self, progress):
        if not isinstance(progress, (int, float)):
            raise ValueError(f"Progress must be an integer or float, got: {type(progress)}")
        self.progress = progress
        if self.progress >= 100:
            self.progress = 100
            self.waiter.set()
        return True

    def use(self, position):
        pass
        # TODO: Implement


class CLIText(CLIItem):
    def __init__(self, name, text=""):
        super().__init__(name)
        self.text = text

    # TODO: Implement

class CLIHelper:
    def __init__(self, ):
        pass
