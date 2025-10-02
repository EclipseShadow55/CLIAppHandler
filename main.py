import threading
from colorama import Fore

class CLIItem:
    def __init__(self, name, **kwargs):
        self._name = name
        self.usages = []
        self.kwargs_handler(**kwargs)

    def kwargs_handler(self, **kwargs):
        pass

    def use(self, handler, position):
        self.usages.append((handler, position))
        return self.get_text(handler, position)

    def get_text(self, handler, position):
        self._text = self.name
        return self._text

    def update(self, changed, new_value):
        for handler, position in self.usages:
            handler.replace(position, original=self._text, new=self.get_text(handler, position))

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        if not isinstance(value, str):
            raise ValueError(f"Name must be a string, got: {type(value)}")
        self._name = value
        self.update('name', value)

class CLILoadingBar(CLIItem):
    def __init__(self, name, progress=None, **kwargs):
        super().__init__(name)
        if progress is None:
            self._progress = self._min_progress
        else:
            if not isinstance(progress, (int, float)):
                raise ValueError(f"Progress must be an integer or float, got: {type(progress)}")
            if progress < self._min_progress or progress > self._max_progress:
                raise ValueError(f"Progress must be between {self._min_progress} and {self._max_progress}, got: {progress}")
            self._progress = progress

    def kwargs_handler(self, **kwargs):
        if 'width' in kwargs and isinstance(kwargs['width'], int):
            self._width = kwargs['width']
        else:
            self._width = 20
        if 'start_char' in kwargs and isinstance(kwargs['start_char'], str):
            self._start_char = kwargs['start_char']
        else:
            self._start_char = '#'
        if 'end_char' in kwargs and isinstance(kwargs['end_char'], str):
            self._end_char = kwargs['end_char']
        else:
            self._end_char = '#'
        if 'empty_char' in kwargs and isinstance(kwargs['empty_char'], str):
            self._empty_char = kwargs['empty_char']
        else:
            self._empty_char = '-'
        if 'full_char' in kwargs and isinstance(kwargs['full_char'], str):
            self._full_char = kwargs['full_char']
        else:
            self._full_char = '='
        if 'prefix' in kwargs and isinstance(kwargs['prefix'], str):
            self._prefix = kwargs['prefix']
        else:
            self._prefix = ''
        if 'suffix' in kwargs and isinstance(kwargs['suffix'], str):
            self._suffix = kwargs['suffix']
        else:
            self._suffix = ''
        if 'done' in kwargs and isinstance(kwargs['done'], str):
            self._done = kwargs['done']
        else:
            self._done = None
        if 'max_progress' in kwargs and isinstance(kwargs['max_progress'], (int, float)):
            self._max_progress = kwargs['max_progress']
        else:
            self._max_progress = 100
        if 'min_progress' in kwargs and isinstance(kwargs['min_progress'], (int, float)):
            self._min_progress = kwargs['min_progress']
        else:
            self._min_progress = 0
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
            self._format_string = '{}: {} {}%'
            self._format_items = ['name', 'bar', 'progress']
            self._inserts = [0, 4, 7]

    def use(self, handler, position):
        self.usages.append((handler, position))
        return self.get_text(handler, position)

    def get_text(self, handler, position):
        if self._done is not None and self.progress >= self._max_progress:
            self._text = self._done
            return self._text
        else:
            processed = self._format_string[:self._inserts[0]]
            for i, item in enumerate(self._format_items):
                if isinstance(item, str):
                    if item == 'name':
                        processed += self.name
                    elif item == 'progress':
                        processed += f"{self.progress:.2f}"
                    elif item == 'bar':
                        filled_length = int(self._width * (self.progress - self._min_progress) / (self._max_progress - self._min_progress))
                        bar = self._full_char * filled_length + self._empty_char * (self._width - filled_length)
                        processed += f"{self._start_char}{bar}{self._end_char}"
                elif isinstance(item, CLIItem):
                    processed += item.use(handler, (position[0] + processed.count('\n'), position[1] if processed.count('\n') == 0 else 0 + len(processed.split('\n')[-1])))
                if i < len(self._inserts) - 1:
                    processed += self._format_string[self._inserts[i] + 2:self._inserts[i + 1]]
                else:
                    processed += self._format_string[self._inserts[i] + 2:]
            self._text = f"{self._prefix}{processed}{self._suffix}"
            return self._text

    def update(self, changed, new_value):
        for handler, position in self.usages:
            handler.replace(position, original=self._text, new=self.get_text(handler, position))

    def __add__(self, other):
        if isinstance(other, (int, float)):
            progress = self.progress + other
            if progress > self._max_progress:
                self._progress = self._max_progress
                self.update('progress', self._progress)
            elif self.progress < self._min_progress:
                self._progress = self._min_progress
                self.update('progress', self._progress)
            else:
                self._progress = progress
                self.update('progress', self._progress)
            return True
        return False

    def __sub__(self, other):
        if isinstance(other, (int, float)):
            progress = self.progress - other
            if progress > self._max_progress:
                self._progress = self._max_progress
                self.update('progress', self._progress)
            elif self.progress < self._min_progress:
                self._progress = self._min_progress
                self.update('progress', self._progress)
            else:
                self._progress = progress
                self.update('progress', self._progress)
            return True
        return False

    @property
    def progress(self):
        return self._progress

    @progress.setter
    def progress(self, value):
        if not isinstance(value, (int, float)):
            return
        if value < self._min_progress or value > self._max_progress:
            return
        self._progress = value
        self.update('progress', value)

    @property
    def width(self):
        return self._width

    @width.setter
    def width(self, value):
        if not isinstance(value, int):
            return
        if value < 1:
            return
        self._width = value
        self.update('width', value)

    @property
    def start_char(self):
        return self._start_char

    @start_char.setter
    def start_char(self, value):
        if not isinstance(value, str):
            return
        self._start_char = value
        self.update('start_char', value)

    @property
    def end_char(self):
        return self._end_char

    @end_char.setter
    def end_char(self, value):
        if not isinstance(value, str):
            return
        self._end_char = value
        self.update('end_char', value)

    @property
    def empty_char(self):
        return self._empty_char

    @empty_char.setter
    def empty_char(self, value):
        if not isinstance(value, str):
            return
        self._empty_char = value
        self.update('empty_char', value)

    @property
    def full_char(self):
        return self._full_char

    @full_char.setter
    def full_char(self, value):
        if not isinstance(value, str):
            return
        self._full_char = value
        self.update('full_char', value)

    @property
    def prefix(self):
        return self._prefix

    @prefix.setter
    def prefix(self, value):
        if not isinstance(value, str):
            return
        self._prefix = value
        self.update('prefix', value)

    @property
    def suffix(self):
        return self._suffix

    @suffix.setter
    def suffix(self, value):
        if not isinstance(value, str):
            return
        self._suffix = value
        self.update('suffix', value)

    @property
    def done(self):
        return self._done

    @done.setter
    def done(self, value):
        if not isinstance(value, str) and value is not None:
            return
        self._done = value
        self.update('done', value)

    @property
    def max_progress(self):
        return self._max_progress

    @max_progress.setter
    def max_progress(self, value):
        if not isinstance(value, (int, float)):
            return
        if value <= self._min_progress:
            return
        self._max_progress = value
        if self._progress > self._max_progress:
            self._progress = self._max_progress
            self.update('progress', self._progress)
        self.update('max_progress', value)

    @property
    def min_progress(self):
        return self._min_progress

    @min_progress.setter
    def min_progress(self, value):
        if not isinstance(value, (int, float)):
            return
        if value >= self._max_progress:
            return
        self._min_progress = value
        if self._progress < self._min_progress:
            self._progress = self._min_progress
            self.update('progress', self._progress)
        self.update('min_progress', value)

    @property
    def format(self):
        return {"format": self._format_string,
                "items":  self._format_items}

    @format.setter
    def format(self, value):
        if not isinstance(value, dict):
            return
        if 'format' in value and 'items' in value:
            if isinstance(value['format'], str) and isinstance(value['items'], list):
                inserts = []
                opened = None
                slashed = False
                processed = -1
                # Process the format string to find all {}
                for i, cha in enumerate(value['format']):
                    if opened is not None:
                        if cha == '}':
                            inserts.append(i - 1)
                            opened = None
                    else:
                        return
                    if not slashed:
                        if cha == '{':
                            opened = i
                        if cha == '\\':
                            slashed = True
                    else:
                        processed = i
                # Process the items to validate them
                if len(inserts) != len(value['items']):
                    return
                for item in value['items']:
                    if not isinstance(item, (str, CLIItem)):
                        return
                    if isinstance(item, str):
                        if item not in ['name', 'progress', 'bar']:
                            return
                self._format_string = value['format']
                self._format_items = value['items']
                self._inserts = inserts
                self.update('format', value)

class CLIText(CLIItem):
    def __init__(self, name, content="", **kwargs):
        super().__init__(name)
        self._content = content

    def use(self, handler, position):
        self.usages.append((handler, position))
        return self.get_text(handler, position)

    def get_text(self, handler, position):
        self._text = self._content
        return self._text

    def update(self, changed, new_value):
        for handler, position in self.usages:
            handler.replace(position, original=self._text, new=self.get_text(handler, position))

    @property
    def content(self):
        return self._content

    @content.setter
    def content(self, value):
        if not isinstance(value, str):
            raise ValueError(f"Content must be a string, got: {type(value)}")
        self._content = value
        self.update('content', value)

class CLIAppHandler:
    def __init__(self):
        self.text = []
        self.queue = []
        self.lock = threading.Lock()

    # TODO: Implement