#! /usr/bin/python
import ConfigParser
import time

DEPLOY_CONFIG_FILE = "config.ini"

deploy_phases = [
    {
        'deploy_type': 'pre-install',
        'deploy_percentage': '10%',
        'deploy_result': 'success',
        'next_deploy_phase': 'first-install'
    },
    {
        'deploy_type': 'first-install',
        'deploy_percentage': '25%',
        'deploy_result': 'success',
        'next_deploy_phase': 'second-install'
    },
    {
        'deploy_type': 'second-install',
        'deploy_percentage': '50%',
        'deploy_result': 'success',
        'next_deploy_phase': 'third-install'
    },
    {
        'deploy_type': 'third-install',
        'deploy_percentage': '75%',
        'deploy_result': 'success',
        'next_deploy_phase': 'last-install'
    },
    {
        'deploy_type': 'last-install',
        'deploy_percentage': '100%',
        'deploy_result': 'success',
    }
]

def deploy_tasks():
    log("=== deploy tasks ===")
    config = ConfigParser.RawConfigParser()
    for phase in deploy_phases:
        section = "deploy_phase_" + str(deploy_phases.index(phase) + 1)
        config.add_section(section)
        for key, value in phase.items():
            config.set(section, key, value)
        with open(DEPLOY_CONFIG_FILE, 'wb') as configfile:
            config.write(configfile)
        time.sleep(2)

def log(content):
    with open("tt.log", 'a+') as f:
        f.write(str(content) + "\n")

