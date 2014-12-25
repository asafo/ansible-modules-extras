#!/usr/bin/python
# -*- coding: utf-8 -*-

"""

Ansible module to manage postgresql replication
2014 (5775), Asaf Ohayon <asaf@hadasa-oss.net>

This file is part of Ansible

Ansible is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Ansible is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.
You should have received a copy of the GNU General Public License
along with Ansible.  If not, see <http://www.gnu.org/licenses/>.
"""

DOCUMENTATION = '''
---
module: postgres_replication

short_description: Manage PostgreSQL replication
description:
    - Manages PostgreSQL streaming replication backup on master, import to standby
version_added: ""
options:
    mode:
        description:
            - module operating mode. Could be backup_sync (pg_start_backup, rsync & pg_stop_backup)
        required: False
        choices:
            - backup_sync
        default: backup_sync
    master_user:
        description:
            - username to connect master host, if defined master_password also needed.
        required: False
    master_password:
        description:
            - password to connect master host, if defined master_user also needed.
        required: False
    master_host:
        description:
            - master host to connect
        required: True
'''

EXAMPLES = '''
# Import base backup from master
- postgresql_replication: mode=backup_sync
'''

try:
    import psycopg2
    import psycopg2.extras
except ImportError:
    postgresqldb_found = False
else:
    postgresqldb_found = True

    # ===========================================
# Module execution.
#

def main():
    module = AnsibleModule(
        argument_spec=dict(
            master_user=dict(default="postgres"),
            master_password=dict(default=""),
            master_host=dict(default=""),
            port=dict(default="5432"),
        ),
        supports_check_mode = True
    )

    if not postgresqldb_found:
        module.fail_json(msg="the python psycopg2 module is required")

    port = module.params["port"]
    changed = False

    # To use defaults values, keyword arguments must be absent, so 
    # check which values are empty and don't include in the **kw
    # dictionary
    params_map = {
        "login_host":"host",
        "login_user":"user",
        "login_password":"password",
        "port":"port"
    }
    kw = dict( (params_map[k], v) for (k, v) in module.params.iteritems() 
              if k in params_map and v != '' )
    try:
        db_connection = psycopg2.connect(database="template1", **kw)
        # Enable autocommit so we can create databases
        if psycopg2.__version__ >= '2.4.2':
            db_connection.autocommit = True
        else:
            db_connection.set_isolation_level(psycopg2
                                              .extensions
                                              .ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = db_connection.cursor(
                cursor_factory=psycopg2.extras.DictCursor)
    except Exception, e:
        module.fail_json(msg="unable to connect to database: %s" % e)

    module.exit_json(changed=changed)

# import module snippets
from ansible.module_utils.basic import *
from ansible.module_utils.database import *
if __name__ == '__main__':
    main()
