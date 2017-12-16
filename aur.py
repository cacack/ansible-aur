#!/usr/bin/env python2

from ansible.module_utils.basic import *


TOOL_TO_INSTALL_CMD_MAP = {
    'pacaur': ['pacaur', '--noconfirm', '--noedit', '-S'],
    'yaourt': ['yaourt', '--noconfirm', '-S'],
}


def package_installed(module, package_name):
    cmd = ['pacman', '-Q', package_name]
    exit_code, _, _ = module.run_command(cmd, check_rc=False)
    return exit_code == 0


def update_packages(module, tool):
    assert tool in TOOL_TO_INSTALL_CMD_MAP

    cmd = TOOL_TO_INSTALL_CMD_MAP[tool] + ['--update']
    rc, stdout, stderr = module.run_command(cmd, check_rc=True)

    module.exit_json(
        changed='there is nothing to do' not in stdout,
        msg='updated packages',
    )


def install_packages(module, package_name, tool):
    if package_installed(module, package_name):
        module.exit_json(
            changed=False,
            msg='package already installed',
        )

    assert tool in TOOL_TO_INSTALL_CMD_MAP

    cmd = TOOL_TO_INSTALL_CMD_MAP[tool] + [package_name]
    module.run_command(cmd, check_rc=True)

    module.exit_json(
        changed=True,
        msg='installed package',
    )


def remove_packages(module, package_name, recurse, nosave):
    if not package_installed(module, package_name):
        module.exit_json(
            changed=False,
            msg='package not installed',
        )

    options = '-R'

    if nosave:
        options += 'n'

    if recurse:
        options += 's'

    cmd = ['pacman', '--noconfirm', options, package_name]
    module.run_command(cmd, check_rc=True)

    module.exit_json(
        changed=True,
        msg='removed package',
    )


def main():
    module = AnsibleModule(
        argument_spec={
            'name': {
                'required': False,
            },
            'state': {
                'default': 'present',
                'choices': ['present', 'absent'],
            },
            'tool': {
                'default': 'pacaur',
                'choices': ['pacaur', 'yaourt'],
            },
            'recurse': {
                'default': True,
                'type': 'bool',
            },
            'nosave': {
                'default': True,
                'type': 'bool',
            },
            'update': {
                'default': False,
                'type': 'bool',
            },
        },
    )

    params = module.params

    if params['update']:
        update_packages(module, params['tool'])
    else:
        if params['state'] == 'present':
            install_packages(module, params['name'], params['tool'])
        elif params['state'] == 'absent':
            remove_packages(module, params['name'], params['recurse'], params['nosave'])


if __name__ == '__main__':
    main()
