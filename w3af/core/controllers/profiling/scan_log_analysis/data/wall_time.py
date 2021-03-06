import re

from utils.utils import epoch_to_string

SCAN_TOOK_RE = re.compile('took (\d*\.\d\d)s to run')
PLUGIN_TOOK_RE = re.compile('\] (.*?)\.(grep|audit|discover)\(.*?\) took (.*?)s to run')


def show_generic_spent_time(scan, name, must_have):
    scan.seek(0)
    spent_time = 0.0

    for line in scan:
        if must_have not in line:
            continue

        match = SCAN_TOOK_RE.search(line)
        if match:
            spent_time += float(match.group(1))

    print('    %s() took %s' % (name, epoch_to_string(spent_time)))


def show_plugin_time(scan_log_filename, scan):
    scan.seek(0)
    spent_time_by_plugin = dict()

    for line in scan:
        if 'took' not in line:
            continue

        match = PLUGIN_TOOK_RE.search(line)
        if not match:
            continue

        plugin_name = match.group(1)
        plugin_type = match.group(2)
        took = float(match.group(3))

        if plugin_type not in spent_time_by_plugin:
            spent_time_by_plugin[plugin_type] = {}
            spent_time_by_plugin[plugin_type][plugin_name] = took

        elif plugin_name not in spent_time_by_plugin[plugin_type]:
            spent_time_by_plugin[plugin_type][plugin_name] = took

        else:
            spent_time_by_plugin[plugin_type][plugin_name] += took

    if not spent_time_by_plugin:
        return

    print('')
    print('Wall time used by plugins:')

    def sort_by_value(a, b):
        return cmp(b[1], a[1])

    for plugin_type in spent_time_by_plugin:
        spent_time_by_plugin_one_type = spent_time_by_plugin[plugin_type]

        l = spent_time_by_plugin_one_type.items()
        l.sort(sort_by_value)
        l = l[:10]

        print('')
        print('Top10 most time consuming %s plugins' % plugin_type)

        for plugin_name, took in l:
            print('    - %s took %s' % (plugin_name, epoch_to_string(took)))


def show_discovery_time(scan_log_filename, scan):
    show_generic_spent_time(scan, 'discover', '.discover(')


def show_audit_time(scan_log_filename, scan):
    show_generic_spent_time(scan, 'audit', '.audit(')


def show_grep_time(scan_log_filename, scan):
    show_generic_spent_time(scan, 'grep', '.grep(')


def show_output_time(scan_log_filename, scan):
    show_generic_spent_time(scan, 'output', '.flush(')
