import subprocess
import re, time, os, sys, msvcrt
import bencode
import codecs
import psutil

from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
import smtplib

from Misc import processArguments


def check_interface(interface_name):
    output = subprocess.check_output("ipconfig /all")

    lines = output.splitlines()
    lines = filter(lambda x: x, lines)

    # print('output: ', output)
    # print('lines: ', lines)

    ip_address = ''
    # mac_address = ''
    name = ''

    for line in lines:
        # -------------
        # Interface Name

        is_interface_name = re.match(r'^[a-zA-Z0-9].*:$', line)
        # is_interface_name = 1
        if is_interface_name:

            # Check if there's previews values, if so - yield them
            if name and ip_address:
                if name == interface_name:
                    return ip_address

            ip_address = ''
            # mac_address = ''
            name = line.rstrip(':')

            # print('line: ', line)
            # print('name: ', name)

        line = line.strip().lower()

        if ':' not in line:
            continue

        value = line.split(':')[-1]
        value = value.strip()

        # -------------
        # IP Address

        is_ip_address = not ip_address and re.match(r'ipv4 address|autoconfiguration ipv4 address|ip address', line)

        if is_ip_address:
            ip_address = value
            ip_address = ip_address.replace('(preferred)', '')
            ip_address = ip_address.strip()

            # print('line: ', line)
            # print('ip_address: ', ip_address)

        # -------------
        # MAC Address

        # is_mac_address = not ip_address and re.match(r'physical address', line)
        #
        # if is_mac_address:
        #     mac_address = value
        #     mac_address = mac_address.replace('-', ':')
        #     mac_address = mac_address.strip()

    if name and ip_address:
        if name == interface_name:
            return ip_address
    return None


if __name__ == '__main__':

    params = {
        'interface_name': 'PPP adapter PureVPN',
        'utorrent_mode': 1,
        'restart_time': 86400,
        'wait_time': 10800,
        'post_wait_time': 10,
        'check_vpn_gap': 30,
        'max_vpn_wait_time': 600,
        'vpn_path': 'C:\Users\Tommy\Desktop\purevpn.lnk',
        'tor_path': 'C:\Users\Tommy\Desktop\uTorrent.lnk',
        'settings_path': 'C:\Users\Tommy\AppData\Roaming\uTorrent\settings.dat',
        'vpn_proc': 'purevpn.exe',
        'tor_proc': 'uTorrent.exe',
        'syatem_name': 'GT1K',
        'email_auth': [],
    }

    processArguments(sys.argv[1:], params)
    utorrent_mode = params['utorrent_mode']
    interface_name = params['interface_name']
    restart_time = params['restart_time']
    wait_time = params['wait_time']
    post_wait_time = params['post_wait_time']
    check_vpn_gap = params['check_vpn_gap']
    vpn_path = params['vpn_path']
    tor_path = params['tor_path']
    settings_path = params['settings_path']
    vpn_proc = params['vpn_proc']
    tor_proc = params['tor_proc']
    email_auth = params['email_auth']
    max_vpn_wait_time = params['max_vpn_wait_time']

    global_start_t = time.time()

    restart_now = 0
    prev_ip_address = ''
    restarted = 1

    while True:

        os.startfile(vpn_path)
        ip_address = None

        print('waiting for vpn to start')
        vpn_wait_start_t = time.time()

        while True:
            ip_address = check_interface(interface_name)
            if ip_address is not None:
                break
            current_t = time.time()
            if current_t - global_start_t > restart_time or current_t - vpn_wait_start_t > max_vpn_wait_time:
                restart_now = 1
                break
            time.sleep(0.1)

        if restart_now:
            break

        print('vpn started with ip_address: {}'.format(ip_address))

        if ip_address != prev_ip_address:
            prev_ip_address = ip_address

            if email_auth:
                fromaddr = email_auth[0]
                toaddr = email_auth[1]
                syatem_name = email_auth[3]
                msg = MIMEMultipart()
                msg['From'] = fromaddr
                msg['To'] = toaddr
                msg['Subject'] = "{} IP Update".format(syatem_name)
                body = ''
                if restarted:
                    restarted = 0
                    body += 'System restarted\n'

                body += "{} IP has been updated to: {}".format(syatem_name, ip_address)

                msg.attach(MIMEText(body, 'plain'))

                server = smtplib.SMTP('smtp.gmail.com', 587)
                server.ehlo()
                server.starttls()
                server.ehlo()
                server.login(fromaddr, email_auth[2])
                text = msg.as_string()
                print('Sending email to {} from {}'.format(toaddr, fromaddr))
                server.sendmail(fromaddr, toaddr, text)

        if utorrent_mode:
            f = codecs.open(settings_path, "rb").read()
            d = bencode.bdecode(f)
            d['net.bind_ip'] = ip_address
            d['net.outgoing_ip'] = ip_address
            f_out = bencode.bencode(d)
            codecs.open(settings_path, "wb").write(f_out)
        else:
            settings_lines = open(settings_path, "r").readlines()
            with open(settings_path, "w") as fid:
                for _line in settings_lines:
                    if _line.startswith('Connection\InterfaceAddress'):
                        _line = 'Connection\InterfaceAddress={}\n'.format(ip_address)
                    fid.write(_line)

        os.startfile(tor_path)

        print('Waiting for {} seconds. Press any key to continue'.format(wait_time))

        for i in xrange(wait_time):
            if (i + 1) % check_vpn_gap == 0:
                ip_address = check_interface(interface_name)
                if ip_address is None:
                    print('\nvpn disconnection detected')
                    break

            if msvcrt.kbhit():
                inp = msvcrt.getch()
                print('\ncontinuing')
                break

            time.sleep(1)
            sys.stdout.write('\r{}'.format(i + 1))
            sys.stdout.flush()

        sys.stdout.write('\n')
        sys.stdout.flush()

        tor_killed = 0
        for proc in psutil.process_iter():
            if proc.name() == tor_proc:
                proc.terminate()
                tor_killed = 1
                break

        if not tor_killed:
            raise IOError('Tor process {} not found'.format(tor_proc))

        vpn_killed = 0
        for proc in psutil.process_iter():
            if proc.name() == vpn_proc:
                proc.kill()
                vpn_killed = 1
                break

        if not vpn_killed:
            raise IOError('VPN process {} not found'.format(vpn_proc))

        if time.time() - global_start_t > restart_time:
            restart_now = 1
            break

        if restart_now:
            break

        print('Waiting for {} seconds. Press any key to continue'.format(post_wait_time))
        for i in xrange(post_wait_time):
            if msvcrt.kbhit():
                inp = msvcrt.getch()
                print('\ncontinuing')
                break

            time.sleep(1)
            sys.stdout.write('\r{}'.format(i + 1))
            sys.stdout.flush()

        sys.stdout.write('\n')
        sys.stdout.flush()

    if restart_now:
        print("Restarting...")
        os.system("shutdown -t 0 -r -f")
