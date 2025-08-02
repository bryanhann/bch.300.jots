#!/usr/bin/env python3
import os
import subprocess
from functools import cache
import sys
import datetime
import inspect
import itertools
from pathlib import Path

@cache
def JOTS():
    acc = []
    a = subprocess.run("bch.zjot show".split(), text=True, capture_output=True)
    for line in a.stdout.split('\n'):
        if line and line[0] in '12':
            acc.append(zjot4line(line))
    return acc


NOW = datetime.datetime.now()
Q_PROMPT=os.environ.get('Q_PROMPT')
Q_PROMPT=Path(Q_PROMPT)

def lmap (*args): return list(map(*args))
def lfilter(*args): return list(filter(*args))
def dt4stamp(stamp): return datetime.datetime.strptime(stamp,"%Y%m%dT%H%M%S")
def zjot4obj(obj): return klass4obj( obj )( obj )
def zjot4line(line): return zjot4obj(obj4line(line))
def is_zjot_class(v): return inspect.isclass(v) and issubclass(v,Zjot)
def good_pair( pair ): return inspect.isclass(pair[1]) and issubclass(pair[1],Zjot)
def good_dict(): return dict( filter( good_pair, globals().items() ) )
def name4obj(obj): return (names4tags(obj.tags) + [''])[0]
def klass4obj(obj): return good_dict().get( name4obj(obj) , Zjot)
def name4tag(tag): return tag[1:-1]
def names4tags(tags): return lmap(name4tag,tags)
def is_tag(tag): return tag.startswith('{') and tag.endswith('}')
def seconds4delta(delta): return delta and int(delta.total_seconds())

def peel_while(fn,parts):
    while parts and fn(parts[0]):
        yield parts.pop(0)

def obj4line(line):
        class Namespace: pass
        self = Namespace()
        self.line = line
        parts = line.split() + ['']
        self.stamp = parts.pop(0)
        self.zjot = parts.pop(0)
        self.tags = list(peel_while(is_tag, parts))
        self.prefix = list(peel_while(lambda x: not x=='|', parts))
        self.content = parts
        return self

class Zjot:
    def __init__(self, obj):
        self._line = obj.line
        self._stamp = obj.stamp
        self._zjot = obj.zjot
        self._tags = obj.tags
        self._prefix = ' '.join(obj.prefix)
        self._content = ' '.join(obj.content)
        self._dt = dt4stamp(self._stamp)
    def __repr__(self):
        klass = self.__class__.__name__
        line = f"{self._dt} {' '.join(self._tags)} {self._prefix} {self._content}"
        line = f"{line:60} --- <{klass}>"
        return line
    def tags(self): return [ x[1:-1] for x in self._tags ] + [''] * 5
    def age(self): return NOW - self._dt
    def time(self): return str(self._dt).split()[1]


class task(Zjot):
    def __init__(self,obj):
        Zjot.__init__(self,obj)
        self._t1 = None
        self._depth = 0
    def report_active(self):
        pad = '  ' * (self._depth)
        print( f"{pad}++{self._prefix}" )

    def report(self): self.report_closed()
    def report_closed(self):
        pad = '  ' * (self._depth)
        seconds = self.seconds() or 0
        print( f"{seconds:5} | {pad}{self._prefix}" )
    def is_push(self): return self._tags[1] == '{+}'
    def is_pop(self): return self._tags[1] == '{-}'
    def is_reset(self): return self._tags[1] == '{reset}'
    def is_active(s): return s.is_push() and not s._t1
    def __repr__(s): return f"{s._prefix} {s._content} : {s.time()} [{s.elapsed()}]"
    def finish(s, other): s._t1 = other._dt
    def push(s,depth): s._depth = depth
    def show(s): print(f"{s._depth} {s}")
    def elapsed(s): return s._t1 and s._t1 - s._dt or None
    def completed(s): return s._t1 is not None
    def set_depth(s,depth): s._depth = depth
    def seconds(s): return seconds4delta(s.elapsed())


def prep_current():
    stack = []
    for task in current_tasks():
        if task.is_push():
            task.set_depth(len(stack))
            stack.append(task)
        elif task.is_pop():
            stack and stack.pop(-1).finish(task)

def is_head(task): return bool(task.is_push())
def heads(): return lfilter(is_head, TASKS())
def is_active(task): return bool(task.is_active())
def heads(): return lfilter(is_head, TASKS())
def actives(): return lfilter(is_active, TASKS())
def dt4line(line): return dt4stamp(stamp4line(line))

def TASKS(): return all_tasks()
@cache
def all_tasks(): return [ x for x in JOTS() if isinstance(x,task) ]

@cache
def resets(): return lfilter( lambda x:x.is_reset(), all_tasks() )

def is_current(task): return task._dt > resets()[-1]._dt

def current_tasks(): yield from filter( is_current, all_tasks() )

######################################################################################
def cmd_foo(*args):
    for zjot in current_tasks():
        print( zjot.age(), zjot.tags()[1], zjot)

def cmd_all(*args): [ task.report() for task in heads() ]
def cmd_default(*args): cmd_active(*args)
def cmd_active(*args):
    for task in actives():
        task.report_active()

def cmd_prompt(*args):
    items = [ task._prefix for task in actives() ]
    line='|'.join(items)
    line = f"{line}"
    Q_PROMPT.write_text(line)

def fn4cmd(cmd):
    try:
        fn = eval( f"cmd_{cmd}" )
    except NameError:
        exit(f'commmand [{cmd}] not found' )
    return fn

def main (cmd='default', *args):
    #prep_buffer()
    fn4cmd(cmd)(args)

if __name__ == '__main__':
    args = sys.argv[1:]
    main(*args)


