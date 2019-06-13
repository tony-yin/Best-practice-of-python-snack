import time
from snack import ButtonBar, TextboxReflowed, GridFormHelp, GridForm, \
    Textbox, CheckboxTree, Listbox, Grid, Entry, Label, types, Scale, \
    SingleRadioButton


def ExtButtonChoiceWindow(screen, title, text,
                          buttons=['Ok', 'Cancel'],
                          width=40, x=None, y=None, help=None):

    bb = ButtonBar(screen, buttons, compact=1)
    t = TextboxReflowed(width, text, maxHeight=screen.height - 12)

    g = GridFormHelp(screen, title, help, 1, 2)
    g.add(t, 0, 0, padding=(0, 0, 0, 1))
    g.add(bb, 0, 1, growx=1)
    return bb.buttonPressed(g.runOnce(x, y))


def ExtAlert(screen, title, msg, width=70):
    return ExtButtonChoiceWindow(screen, title, msg, ["Ok"], width)


def ExtCheckboxWindow(screen, title, text, items,
                      buttons=('Ok', 'Cancel'), width=50, height=8):

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
                           buttons=('Ok', 'Cancel'),
                           width=40, scroll=0, height=-1,
                           default=None, help=None):

    if (height == -1):
        height = len(items)

    bb = ButtonBar(screen, buttons, compact=1)
    t = TextboxReflowed(width, text)
    lb = Listbox(height, scroll=scroll, returnExit=1)
    count = 0
    for item in items:
        if isinstance(item, types.TupleType):
            (text, key) = item
        else:
            text = item
            key = count

        if (default == count):
            default = key
        elif (default == item):
            default = key

        lb.append(text, key)
        count = count + 1

    if (default is not None):
        lb.setCurrent(default)

    g = GridFormHelp(screen, title, help, 1, 3)
    g.add(t, 0, 0)
    g.add(lb, 0, 1, padding=(0, 1, 0, 1))
    g.add(bb, 0, 2, growx=1)

    rc = g.runOnce()

    return (rc, bb.buttonPressed(rc), lb.current())


def ExtEntryWindow(screen, title, text, prompts,
                   allowCancel=1, width=40, entryWidth=20,
                   buttons=['Ok', 'Cancel'], help=None):

    bb = ButtonBar(screen, buttons, compact=1)
    t = TextboxReflowed(width, text)

    count = 0
    for n in prompts:
        count = count + 1

    sg = Grid(2, count)

    count = 0
    entryList = []
    for n in prompts:
        if isinstance(n, types.TupleType):
            (n, e) = n
            if (type(e) in types.StringTypes):
                e = Entry(entryWidth, e)
        else:
            e = Entry(entryWidth)

        sg.setField(Label(n), 0, count, padding=(0, 0, 1, 0), anchorLeft=1)
        sg.setField(e, 1, count, anchorLeft=1)
        count = count + 1
        entryList.append(e)

    g = GridFormHelp(screen, title, help, 1, 3)

    g.add(t, 0, 0, padding=(0, 0, 0, 1))
    g.add(sg, 0, 1, padding=(0, 0, 0, 1))
    g.add(bb, 0, 2, growx=1)

    result = g.runOnce()

    entryValues = []
    count = 0
    for n in prompts:
        entryValues.append(entryList[count].value())
        count = count + 1

    return (result, bb.buttonPressed(result), tuple(entryValues))


def ExtPwdEntryWindow(screen, title, text, prompts,
                      allowCancel=1, width=40, entryWidth=20,
                      buttons=['Ok', 'Cancel'], help=None):

    bb = ButtonBar(screen, buttons, compact=1)
    t = TextboxReflowed(width, text)

    count = 0
    for n in prompts:
        count = count + 1

    sg = Grid(2, count)

    count = 0
    entryList = []
    for n in prompts:
        if isinstance(n, types.TupleType):
            (n, e) = n
            if (type(e) in types.StringTypes):
                e = Entry(entryWidth, e, password=1)
        else:
            e = Entry(entryWidth, password=1)

        sg.setField(Label(n), 0, count, padding=(0, 0, 1, 0), anchorRight=1)
        sg.setField(e, 1, count, anchorLeft=1)
        count = count + 1
        entryList.append(e)

    g = GridFormHelp(screen, title, help, 1, 3)

    g.add(t, 0, 0, padding=(0, 0, 0, 1))
    g.add(sg, 0, 1, padding=(0, 0, 0, 1))
    g.add(bb, 0, 2, growx=1)

    result = g.runOnce()

    entryValues = []
    count = 0
    for n in prompts:
        entryValues.append(entryList[count].value())
        count = count + 1

    return (result, bb.buttonPressed(result), tuple(entryValues))


def ExtEntryRadioWindow(screen, title, text, prompts,
                        allowCancel=1, width=40, entryWidth=20,
                        buttons=['Ok', 'Cancel'], help=None, radio_prompts=''):

    bb = ButtonBar(screen, buttons, compact=1)
    t = TextboxReflowed(width, text)
    radio_grid = Grid(3, len(radio_prompts))
    sg = Grid(2, len(prompts))

    max_name_length = 0
    for n in prompts:
        if isinstance(n, types.TupleType):
            n = n[0]
        if len(n) > max_name_length:
            max_name_length = len(n)

    radioList = parse_radio_prompts(radio_prompts, radio_grid, entryWidth,
                                    max_name_length)
    entryList = []
    entry_row = 0
    for n in prompts:
        if isinstance(n, types.TupleType):
            (n, e) = n
            if (type(e) in types.StringTypes):
                e = Entry(entryWidth, e)
        else:
            e = Entry(entryWidth)

        sg.setField(Label(n), 0, entry_row, padding=(0, 0, 1, 0), anchorLeft=1)
        sg.setField(e, 1, entry_row, anchorLeft=1)
        entry_row += 1
        entryList.append(e)

    g = GridFormHelp(screen, title, help, 1, 4)
    g.add(t, 0, 0, padding=(0, 0, 0, 1))
    g.add(radio_grid, 0, 1, padding=(0, 0, 0, 1))
    g.add(sg, 0, 2, padding=(0, 0, 0, 1))
    g.add(bb, 0, 3, growx=1)

    result = g.runOnce()

    entryValues = []
    for rowRadioList in radioList:
        for radio, radio_text in rowRadioList:
            if radio.selected():
                entryValues.append(radio_text)
                break
    for entry in entryList:
        entryValues.append(entry.value())

    return (result, bb.buttonPressed(result), tuple(entryValues))


def parse_radio_prompts(radio_prompts, radio_grid, entryWidth,
                        max_name_length):
    radioList = []
    radio_row = 0
    for n in radio_prompts:
        label_text, radio_text_list, on_radio_text = n
        group = None
        radio_column = 1
        row_radio_list_length = len(radio_text_list)
        rowRadioList = []
        for radio_text in radio_text_list:
            is_on = 1 if radio_text == on_radio_text else 0
            r = SingleRadioButton(radio_text, group, is_on)
            group = r
            radio_text_length = 4 + len(radio_text)
            radio_right_padding = (entryWidth / row_radio_list_length) - \
                radio_text_length
            remainder = entryWidth % row_radio_list_length
            if remainder != 0 and row_radio_list_length == radio_column:
                radio_right_padding = radio_right_padding + remainder
            radio_grid.setField(r, radio_column, radio_row,
                                padding=(0, 0, radio_right_padding, 0),
                                anchorLeft=1)
            radio_column += 1
            rowRadioList.append((r, radio_text))

        label_text_length = len(label_text)
        label_right_padding = max_name_length - label_text_length + 1
        radio_grid.setField(Label(label_text), 0, radio_row,
                            padding=(0, 0, label_right_padding, 0),
                            anchorLeft=1)
        radio_row += 1
        radioList.append(rowRadioList)
    return radioList


class ExtProgressWindow:

    def __init__(self, screen, title, text):
        self.screen = screen
        self.g = GridForm(self.screen, title, 1, 2)
        self.s = Scale(70, 100)
        self.t = Textbox(70, 12, text)
        self.g.add(self.t, 0, 0)
        self.g.add(self.s, 0, 1)

    def show(self):
        self.g.draw()
        self.screen.refresh()

    def update(self, progress, text=''):
        self.s.set(progress)
        self.t.setText(text)
        self.g.draw()
        self.screen.refresh()

    def close(self):
        time.sleep(1)
        self.screen.popWindow()


class ExtTopProgressWindow:

    def __init__(self, screen, title, text):
        self.screen = screen
        self.g = GridForm(self.screen, title, 1, 2)
        self.s = Scale(70, 100)
        self.t = Textbox(70, 12, text)
        self.g.add(self.s, 0, 0)
        self.g.add(self.t, 0, 1, padding=(0, 1, 0, 0))

    def show(self):
        self.g.draw()
        self.screen.refresh()

    def update(self, progress, text=''):
        self.s.set(progress)
        self.t.setText(text)
        self.g.draw()
        self.screen.refresh()

    def close(self):
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
