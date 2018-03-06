from charms.layer.hookenv import container_spec_set
from charms.reactive import when, when_not
from charms.reactive.flags import set_flag
from charmhelpers.core.hookenv import log, metadata, status_set, config
from string import Template


@when_not('mysql.available')
def motion_blocked():
    status_set('blocked', 'Waiting for database')


@when_not('motion.configured')
@when('mysql.available')
def config_motion(mysql):
    status_set('maintenance', 'Configuring motion container')

    log('dbname {0}'.format(mysql.database()))
    log('host {0}'.format(mysql.host()))
    log('port {0}'.format(mysql.port()))
    log('user {0}'.format(mysql.user()))
    log('password {0}'.format(mysql.password()))

    spec = make_container_spec(mysql)
    log('set container spec:\n{}'.format(spec))
    container_spec_set(spec)

    set_flag('motion.configured')
    status_set('maintenance', 'Creating motion container')


def make_container_spec(dbcfg):
    spec_file = open('reactive/spec_template.yaml')
    pod_spec_template = Template(spec_file.read())

    md = metadata()
    cfg = config()

    data = {
        'name': md.get('name'),
        'image': cfg.get('image'),
        'port': cfg.get('live_port'),
        'camera_url': cfg.get('camera_url'),
        'target_dir': cfg.get('target_dir'),
        'db_dbname': dbcfg.database(),
        'db_host': dbcfg.host(),
        'db_user': dbcfg.user(),
        'db_pass': dbcfg.password(),
        'db_port': dbcfg.port()
    }

    log('using data:\n{}'.format(data))
    return pod_spec_template.substitute(data)
