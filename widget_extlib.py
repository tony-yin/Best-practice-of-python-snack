import time
from snack import *


def ExtButtonChoiceWindow(screen, title, text,
                buttons = [ 'Ok', 'Cancel' ],
                width = 40, x = None, y = None, help = None):

    bb = ButtonBar(screen, buttons, compact=1)
    t = TextboxReflowed(width, text, maxHeight = screen.height - 12)

    g = GridFormHelp(screen, title, help, 1, 2)
    g.add(t, 0, 0, padding = (0, 0, 0, 1))
    g.add(bb, 0, 1, growx = 1)
    return bb.buttonPressed(g.runOnce(x, y))


def ExtAlert(screen, title, msg, width=70):
    return ExtButtonChoiceWindow(screen, title, msg, ["Ok"], width)


def ExtCheckboxWindow(screen, title, text, items,
                buttons = ('Ok', 'Cancel'), width = 50, height=8):

    g = GridForm(screen, title, 1, 3)
    g.add(Textbox(width, 2, text), 0, 0)

    scroll = 0
    if len(items) > height:
        scroll = 1

    ct = CheckboxTree(height, scroll, width)
    if len(items) > 0:
        for i in items:
            ct.append(i, i, items[i])
        g.add(ct, 0, 1)

    bb = ButtonBar(screen, buttons, compact=1)
    g.add(bb, 0, 2, (0, 2, 0, 0), growx=1, growy=1)

    result = g.runOnce()
    return bb.buttonPressed(result), ct.getSelection()


def ExtListboxChoiceWindow(screen, title, text, items,
                buttons = ('Ok', 'Cancel'),
                width = 40, scroll = 0, height = -1,
                default = None, help = None):

    if (height == -1): height = len(items)

    bb = ButtonBar(screen, buttons, compact=1)
    t = TextboxReflowed(width, text)
    l = Listbox(height, scroll = scroll, returnExit = 1)
    count = 0
    for item in items:
        if (type(item) == types.TupleType):
            (text, key) = item
        else:
            text = item
            key = count

        if (default == count):
            default = key
        elif (default == item):
            default = key

        l.append(text, key)
        count = count + 1

    if (default != None):
        l.setCurrent (default)

    g = GridFormHelp(screen, title, help, 1, 3)
    g.add(t, 0, 0)
    g.add(l, 0, 1, padding = (0, 1, 0, 1))
    g.add(bb, 0, 2, growx = 1)

    rc = g.runOnce()

    return (rc, bb.buttonPressed(rc), l.current())


def ExtEntryWindow(screen, title, text, prompts,
        allowCancel = 1, width = 40, entryWidth = 20,
        buttons = [ 'Ok', 'Cancel' ], help = None):

    bb = ButtonBar(screen, buttons, compact=1);
    t = TextboxReflowed(width, text)

    count = 0
    for n in prompts:
        count = count + 1

    sg = Grid(2, count)

    count = 0
    entryList = []
    for n in prompts:
        if (type(n) == types.TupleType):
            (n, e) = n
            if (type(e) in types.StringTypes):
                e = Entry(entryWidth, e)
        else:
            e = Entry(entryWidth)

        sg.setField(Label(n), 0, count, padding = (0, 0, 1, 0), anchorLeft = 1)
        sg.setField(e, 1, count, anchorLeft = 1)
        count = count + 1
        entryList.append(e)

    g = GridFormHelp(screen, title, help, 1, 3)

    g.add(t, 0, 0, padding = (0, 0, 0, 1))
    g.add(sg, 0, 1, padding = (0, 0, 0, 1))
    g.add(bb, 0, 2, growx = 1)

    result = g.runOnce()

    entryValues = []
    count = 0
    for n in prompts:
        entryValues.append(entryList[count].value())
        count = count + 1

    return (result, bb.buttonPressed(result), tuple(entryValues))


def ExtPwdEntryWindow(screen, title, text, prompts,
        allowCancel = 1, width = 40, entryWidth = 20,
        buttons = [ 'Ok', 'Cancel' ], help = None):

    bb = ButtonBar(screen, buttons, compact=1);
    t = TextboxReflowed(width, text)

    count = 0
    for n in prompts:
        count = count + 1

    sg = Grid(2, count)

    count = 0
    entryList = []
    for n in prompts:
        if (type(n) == types.TupleType):
            (n, e) = n
            if (type(e) in types.StringTypes):
                e = Entry(entryWidth, e, password = 1)
        else:
            e = Entry(entryWidth, password = 1)

        sg.setField(Label(n), 0, count, padding=(0, 0, 1, 0), anchorRight=1)
        sg.setField(e, 1, count, anchorLeft=1)
        count = count + 1
        entryList.append(e)

    g = GridFormHelp(screen, title, help, 1, 3)

    g.add(t, 0, 0, padding = (0, 0, 0, 1))
    g.add(sg, 0, 1, padding = (0, 0, 0, 1))
    g.add(bb, 0, 2, growx = 1)

    result = g.runOnce()

    entryValues = []
    count = 0
    for n in prompts:
        entryValues.append(entryList[count].value())
        count = count + 1

    return (result, bb.buttonPressed(result), tuple(entryValues))


class ExtProgressWindow:

    def __init__(self, screen, title, text):
        self.screen = screen
        self.g = GridForm(self.screen, title, 1, 2)
        self.s = Scale(70, 100)
        self.t = Textbox(70, 5, text)
        self.g.add(self.t, 0, 0)
        self.g.add(self.s, 0, 1)

    def show(self):
        self.g.draw()
        self.screen.refresh()

    def update(self, progress, text = ''):
        self.s.set(progress)
        self.t.setText(text)
        self.g.draw()
        self.screen.refresh()

    def close(self):
        self.update(100)
        time.sleep(1)
        self.screen.popWindow()


class ExtTextWindow:

    def __init__(self, screen, title, text):
        self.screen = screen
        self.g = GridForm(screen, title, 1, 1)
        self.g.add(Textbox(60, 2, text), 0, 0)

    def show(self):
        self.g.draw()
        self.screen.refresh()

    def close(self):
        self.screen.popWindow()
