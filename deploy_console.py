#! /usr/bin/python
#encoding=utf-8
__author__ = 'hui.yin@uniswdc.com'

import sys
import traceback
import time
import re
import threading
import subprocess
import ConfigParser
import copy
from snack import *
from set_hostname_ssh_parms import load_c15000_config
from set_vizion_deploy_parms import generate_vizion_json

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

    def update(self, progress, text):
        self.s.set(progress)
        self.t.setText(text)
        self.g.draw()
        self.screen.refresh()

    def close(self):
        time.sleep(1)
        self.screen.popWindow()

class Install_progress:

    def __init__(self):
        self.config_file = DEPLOY_CONFIG_FILE
        self.config_read = ConfigParser.RawConfigParser()
        self.config_read.read(self.config_file)
        self.sections = self.config_read.sections()
        self.lastest_section = self.sections[-1]

    def get_progress_value(self):
        progress_value = self.config_read.get(
            self.lastest_section,
            'deploy_percentage'
        )
        return int(progress_value[:-1])

    def get_current_job_name(self):
        current_job = None
        progress_value = self.get_progress_value()
        if progress_value != 100:
            current_job = self.config_read.get(
                self.lastest_section,
                'next_deploy_phase'
            )
        return current_job

    def get_deploy_info(self):
        info = []
        for section in self.sections:
            name = self.config_read.get(section, 'deploy_type')
            ret = self.config_read.get(section, 'deploy_result')
            info.append("{}: {}".format(name, ret))

        current_job = self.get_current_job_name()
        if current_job:
            info.append("{}: {}".format(current_job, 'running'))

        return info

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

def ExtAlert(screen, title, msg, width=70):
    return ExtButtonChoiceWindow(screen, title, msg, ["Ok"], width)

def ExtButtonChoiceWindow(screen, title, text,
                buttons = [ 'Ok', 'Cancel' ],
                width = 40, x = None, y = None, help = None):

    bb = ButtonBar(screen, buttons, compact=1)
    t = TextboxReflowed(width, text, maxHeight = screen.height - 12)

    g = GridFormHelp(screen, title, help, 1, 2)
    g.add(t, 0, 0, padding = (0, 0, 0, 1))
    g.add(bb, 0, 1, growx = 1)
    return bb.buttonPressed(g.runOnce(x, y))

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

def ExtButtonChoiceWindow(screen, title, text,
                buttons = [ 'Ok', 'Cancel' ],
                width = 40, x = None, y = None, help = None):

    bb = ButtonBar(screen, buttons, compact=1)
    t = TextboxReflowed(width, text, maxHeight = screen.height - 12)

    g = GridFormHelp(screen, title, help, 1, 2)
    g.add(t, 0, 0, padding = (0, 0, 0, 1))
    g.add(bb, 0, 1, growx = 1)
    return bb.buttonPressed(g.runOnce(x, y))

def validate_ip_format(ip):
    p = re.compile('^((25[0-5]|2[0-4]\d|[01]?\d\d?)\.){3}(25[0-5]|2[0-4]\d|[01]?\d\d?)$')
    if p.match(ip):
        return True
    else:
        button = ExtAlert(
            screen,
            "Error",
            "IP format error, please verify your IP!"
        )
        return False

def validate_ip_duplicate(ip, config_type):
    result = True
    ips = get_ips(config_type)
    if ip in ips:
        button = ExtAlert(
            screen,
            "Error",
            "IP duplicate error, {} already exists!".format(ip)
        )
        result = False
    return result

def validate_not_empty(host):
    result = True
    for item in host:
        if not item:
            result = False
            break
    if not result:
        button = ExtAlert(
            screen,
            "Error",
            "Empty error, please supply for each host info!",
        )
    return result

def get_host_empty_items(hosts):
    empty_host = {}
    for host in hosts:
        ip = host["IP Address"]
        items = []
        for k, v in host.items():
            if not v:
                items.append(k)
        if items:
            empty_host[ip] = items

    return empty_host

def get_empty_data():
    items = []
    for k, v in Global_Config.items():
        if not v:
            items.append(k)

    empty_data = {
        "Basic Config": get_host_empty_items(Basic_Config),
        "Additional Config": get_host_empty_items(Additional_Config),
        "Global Config": items
    }
    return empty_data

def check_if_exist_empty():
    empty_data = get_empty_data()
    exist_empty = False
    for v in empty_data.values():
        if v:
            exist_empty = True
            break
    return exist_empty

def get_empty_text():
    empty_data = get_empty_data()
    items = ""
    for key in All_Config_Map.keys():
        settings = empty_data[key]
        if not settings:
            continue
        items += "\n\n" + key + ": "
        if key == "Global Config":
            items += "\n\t" + ", ".join(settings)
            continue
        for k, v in settings.items():
            items += "\n\t" + k + ": " + ", ".join(v)

    data = "Following info can not be empty!{}" \
        .format(items)
    return data

def get_all_display_data():
    items = "All configuration are displayed below. Are you sure to start deploy?\n"
    for k, v in All_Config_Map.items():
        items += "\n" + k + ": \n\t"
        if k == "Global Config":
            items +=  ", ".join(v.values()) + "\n"
            continue
        for host in v:
            items += host["IP Address"] + ": "
            for key, value in host.items():
                if key != "IP Address":
                    items += value + ", "
            items = items[:-2] + "\n\t"

    return items

def get_format_data(data, config_type):
    if config_type == BASIC_TYPE:
        seq = [
            'IP Address',
            'Hostname',
            'Password'
        ]
    elif config_type == ADDITIONAL_TYPE:
        seq = [
            'IP Address',
            'Hostname',
            'Password',
            'Devices'
        ]
    elif config_type == GLOBAL_TYPE:
        seq = [
            'Ntpserver',
            'IP Range'
        ]

    format_data = []
    for s in seq:
        format_data.append((s + ":", data[s]))
    return format_data

def get_basic_format_config():
    key_map = {
        'IP Address': 'ipaddr',
        'Hostname': 'hostname',
        'Password': 'password'
    }
    data = {'ssh': {}}
    for host in Basic_Config:
        data['ssh'][host['IP Address']] = {}
        for k, v in host.items():
            data['ssh'][host['IP Address']][key_map[k]] = v

    return data

def get_additional_format_config():
    key_map = {
        'IP Address': 'ipaddr',
        'Hostname': 'hostname',
        'Password': 'password',
        'Ntpserver': 'ntpserver',
        'IP Range': 'ip_range'
    }
    data = []
    for host in Additional_Config:
        item = {}
        for k, v in Global_Config.items():
            item[key_map[k]] = v
        for k, v in host.items():
            if k == "Devices" and v != '':
                devices = v.split(',')
                for device in devices:
                    key = 'device' + str(devices.index(device) + 1)
                    item[key] = device
            else:
                item[key_map[k]] = v
        data.append(item)

    return data

def start_deploy():
    load_c15000_config(
        deploy_type="console", data=get_basic_format_config()
    )

    generate_vizion_json(
        deploy_type="console", data=get_additional_format_config()
    )

    do_shell("bash {}".format(DEPLOY_SCRIPT_FILE))

def do_shell(cmd):
    p = subprocess.Popen(
        [cmd], stdout=subprocess.PIPE, shell=True
    )
    output, err = p.communicate()
    while p.poll() is None:
        try:
            proc = psutil.Process(p.pid)
            for c in proc.children(recursive=True):
                c.kill()
            proc.kill()
        except psutil.NoSuchProcess:
            pass
    if p.returncode == 1:
        sys.exit(0)
    return output


def get_ips(config_type):
    if config_type == BASIC_TYPE:
        hosts = Basic_Config
    elif config_type == ADDITIONAL_TYPE:
        hosts = Additional_Config
    ips = [host['IP Address'] for host in hosts]
    return ips

def Basic_Host_Window(current, data=None):
    buttons = [ 'save', 'cancel', 'exit']
    if not data:
        data = ['IP Address:', 'Hostname:', 'Password:']
        if current != 'add':
            data = get_format_data(Basic_Config[current], BASIC_TYPE)
            buttons.insert(1, 'Delete')

    host = ExtEntryWindow(
        screen,
        '{} host'.format('Add' if current == 'add' else 'Edit'),
        'Please fill storage host info.',
        data,
        width = 40,
        entryWidth = 40,
        buttons = buttons
    )

    if host[1] == "exit":
        screen.finish()
        return
    elif host[1] == "save":
        new_host = {
            'IP Address': host[2][0],
            'Hostname': host[2][1],
            'Password': host[2][2]
        }
        if not validate_ip_format(host[2][0]):
            return Basic_Host_Window(
                current, get_format_data(new_host, BASIC_TYPE)
            )

        if not validate_not_empty(host[2]):
            return Basic_Host_Window(
                current, get_format_data(new_host, BASIC_TYPE)
            )

        if current == "add":
            if not validate_ip_duplicate(host[2][0], BASIC_TYPE):
                return Basic_Host_Window(
                    current, get_format_data(new_host, BASIC_TYPE)
                )
            Basic_Config.append(new_host)
        else:
            Basic_Config[current] = new_host
    elif host[1] == "delete":
        button = ExtButtonChoiceWindow(
            screen,
            'Delete host',
            'Are you sure to delete current host?'
        )
        if button == "ok":
            del(Basic_Config[current])
        else:
            Basic_Host_Window(current)
    Basic_Config_Window()

def Additional_Host_Window(current, data=None):
    buttons = [ 'Save', 'Cancel', "Exit"]
    if not data:
        data = [
            'IP Address:',
            'Hostname:',
            'Password:',
            'Devices:'
        ]
        if current != 'add':
            data = get_format_data(Additional_Config[current], ADDITIONAL_TYPE)
            buttons.insert(1, 'Delete')
    host = ExtEntryWindow(
        screen,
        '{} host'.format('Add' if current == 'add' else 'Edit'),
        'Please fill search host info.',
        data,
        width = 40,
        entryWidth = 40,
        buttons = buttons
    )

    if host[1] == "exit":
        screen.finish()
        return
    elif host[1] == "save":
        new_host = {
            'IP Address': host[2][0],
            'Hostname': host[2][1],
            'Password': host[2][2],
            'Devices': host[2][3],
        }
        if not validate_ip_format(host[2][0]):
            return Additional_Host_Window(
                current, get_format_data(new_host, ADDITIONAL_TYPE)
            )

        if not validate_not_empty(host[2]):
            return Additional_Host_Window(
                current, get_format_data(new_host, ADDITIONAL_TYPE)
            )

        if current == "add":
            if not validate_ip_duplicate(host[2][0], ADDITIONAL_TYPE):
                return Additional_Host_Window(
                    current, get_format_data(
                        new_host, ADDITIONAL_TYPE)
                )
            Additional_Config.append(new_host)
        else:
            Additional_Config[current] = new_host
    elif host[1] == "delete":
        button = ExtButtonChoiceWindow(
            screen,
            'Delete host',
            'Are you sure to delete current host?'
        )
        if button == "ok":
            del(Additional_Config[current])
        else:
            Additional_Host_Window(current)
    Additional_Config_Window()

def Deploy_Progress_Window():
    a = threading.Thread(target = start_deploy)
    a.start()
    progress = ExtProgressWindow(
        screen,
        "CG20 Deploy",
        "Start deploy CG20 ..."
    )
    progress.show()
    last_progress_value = ""
    while True:
        install_info = Install_progress()
        progress_value = install_info.get_progress_value()
        detail_info = install_info.get_deploy_info()
        if progress_value != last_progress_value:
            progress.update(
                progress_value, "\n".join(detail_info) + "\n\n"
            )
        last_progress_value = progress_value
        state = ""
        for phase in detail_info:
            state = phase.split(':')[1].strip()
            if state == "failed":
                break
        if progress_value == "100" or state == "failed":
            break
    progress.close()
    Deploy_Result_Window(detail_info)

def Deploy_Result_Window(info):
    button = ExtAlert(
        screen,
        'Deploy Result',
        "\n".join(info)
    )
    if button == "ok":
        screen.finish()
        return

def Import_Basic_Config_Window():
    info_level = 'Info'
    success = []
    fail = []
    ips = get_ips(ADDITIONAL_TYPE)
    for host in Basic_Config:
        if host['IP Address'] in ips:
            fail.append(host['IP Address'])
        else:
            success.append(host['IP Address'])
            new_host = copy.copy(host)
            new_host['Devices'] = ''
            Additional_Config.append(new_host)

    info = "Import successfully:{}".format(
        "\n\t" + "\n\t".join(success))
    if fail:
        info_level = "Warning"
        info += "\n\nImport failed: Already exists!{}".format(
            "\n\t" + "\n\t".join(fail))

    button = ExtAlert(
        screen,
        '{}: Import Basic Settings'.format(info_level),
        info
    )
    if button == "ok":
        Additional_Config_Window()

def Global_Config_Window():
    data = get_format_data(Global_Config, GLOBAL_TYPE)
    ret, button, settings = ExtEntryWindow(
        screen,
        'Global Config',
        'Ntpserver format is the same as ip. IP Range format is like x.x.x.x-x, such as "192.168.1.1-5"',
        data,
        buttons = [ 'save', 'cancel', 'exit'],
        width = 60,
    )

    if button == "exit":
        screen.finish()
        return
    if button == "save":
        Global_Config['Ntpserver'] = settings[0]
        Global_Config['IP Range'] = settings[1]
    Additional_Config_Window()

def Welcome_Deploy_Window():
    title = "Welcome Page"
    msg = "Welcome to CG20 deploy. The CG20 is a distributed storage system with a distributed search engine."
    buttons = ['next', 'exit']
    button = ExtButtonChoiceWindow(screen, title, msg, buttons)
    if button == "next":
        Basic_Config_Window()
    elif button == "exit":
        screen.finish()
        return

def Basic_Config_Window():
    ips = [('Add new host', 'add')]
    for host in Basic_Config:
        ips.append((host['IP Address'], Basic_Config.index(host)))

    ret, button, lb = ExtListboxChoiceWindow(
        screen,
        'Distribute Storage Config',
        'Distribute Storage Config',
        ips,
        buttons=("prev", "next", "exit"),
        width=50,
        height=5,
    )

    if button == "exit":
        screen.finish()
        return
    elif button == "prev":
        Welcome_Deploy_Window()
    elif button == "next":
        Additional_Config_Window()
    elif lb is not None:
        Basic_Host_Window(lb)

def Additional_Config_Window():
    ips = [('Add new host', 'add')]
    for host in Additional_Config:
        ips.append((host['IP Address'], Additional_Config.index(host)))

    ret, button, lb = ExtListboxChoiceWindow(
        screen,
        'Distribute Search Config',
        'Distribute Search Config',
        ips,
        buttons=("prev", "next", "import", "global settings", "exit"),
        width=50,
        height=5,
    )

    if button == "exit":
        screen.finish()
        return ''
    elif button == "prev":
        Basic_Config_Window()
    elif button == "next":
        if not Basic_Config or not Additional_Config:
            button = ExtAlert(
                screen,
                'Error',
                "Storage and search config can not be empty!"
            )
            if button == "ok":
                Additional_Config_Window()
        if check_if_exist_empty():
            button = ExtAlert(
                screen,
                'Error',
                get_empty_text(),
                width = 60
            )
            if button == "ok":
                Additional_Config_Window()
        else:
            text = get_all_display_data()
            button = ExtButtonChoiceWindow(
                screen, 'Confirm', text, width=80
            )
            if button == "ok":
                Deploy_Progress_Window()
            elif button == "cancel":
                Additional_Config_Window()
    elif button == "import":
        Import_Basic_Config_Window()
    elif button == "global settings":
        Global_Config_Window()
    elif lb is not None:
        Additional_Host_Window(lb)

def main():
    try:
        Welcome_Deploy_Window()
    except:
        print traceback.format_exc()
    finally:
        screen.finish()
        return ''

def log(content):
    with open("tt.log", 'a+') as f:
        f.write(str(content) + "\n")

DEPLOY_SCRIPT_FILE = "/home/cg20/install.sh"
DEPLOY_CONFIG_FILE = "/opt/cg20_deploy_config.ini"
BASIC_TYPE = 0
ADDITIONAL_TYPE = 1
GLOBAL_TYPE = 2
Basic_Config = []
Additional_Config = []
Global_Config = {
    'Ntpserver': '',
    'IP Range': ''
}
All_Config_Map = {
    'Basic Config': Basic_Config,
    'Additional Config': Additional_Config,
    'Global Config': Global_Config
}
screen = SnackScreen()
main()
