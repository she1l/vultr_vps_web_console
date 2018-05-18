#!/usr/bin/env python
# coding: utf-8

from flask import Flask, render_template, request, Response, jsonify
import requests
import commands

headers = {
    'api_key': 'YOUR_API_KEY',
}

servers = {
    '12956058': 'vultr.guest',
}


def list_server():
    get = requests.get('https://api.vultr.com/v1/server/list', params=headers)
    data = get.json()
    tmp = []
    for key in data:
        tmp.append([data[key]["SUBID"], data[key]["location"], data[key]["DCID"], data[key]["main_ip"]])
    return tmp


def list_ip():
    get = requests.get('https://api.vultr.com/v1/reservedip/list', params=headers)
    data = get.json()
    tmp = []
    for key in data:
        tmp.append([data[key]["DCID"], data[key]["subnet"], data[key]["attached_SUBID"]])
    return tmp


def attach_ip(ip, subid):
    params = {
        'ip_address': ip,
        'attach_SUBID': subid
    }
    post = requests.post(url='https://api.vultr.com/v1/reservedip/attach', params=headers, data=params)
    if str(post.status_code) == '200':
        salt_add_ip(ip, subid)
        return [['Status: ' + str(post.status_code)], ]
    else:
        return [['Status: ' + str(post.status_code) + ' ' + str(post.text)], ]


def detach_ip(ip, subid):
    params = {
        'ip_address': ip,
        'detach_SUBID': subid
    }
    post = requests.post(url='https://api.vultr.com/v1/reservedip/detach', params=headers, data=params)
    if str(post.status_code) == '200':
        salt_delete_ip(ip, subid)
        return [['Status: ' + str(post.status_code)], ]
    else:
        return [['Status: ' + str(post.status_code) + ' ' + str(post.text)], ]


def destroy_ip(ip):
    params = {
        'ip_address': ip,
    }
    post = requests.post(url='https://api.vultr.com/v1/reservedip/destroy', params=headers, data=params)
    if str(post.status_code) == '200':
        return [['Status: ' + str(post.status_code)], ]
    else:
        return [['Status: ' + str(post.status_code) + ' ' + str(post.text)], ]


def create_ip(dcid, ip_type):
    params = {
        'DCID': dcid,
        'ip_type': ip_type
    }
    post = requests.post(url='https://api.vultr.com/v1/reservedip/create', params=headers, data=params)
    if str(post.status_code) == '200':
        return [['Status: ' + str(post.status_code)], ]
    else:
        return [['Status: ' + str(post.status_code) + ' ' + str(post.text)], ]


def salt_add_ip(ip, subid):
    command = 'salt "%s" cmd.run "ip addr add %s dev eth0"' % (servers.get(subid), (ip+'/32'))
    (_, result) = commands.getstatusoutput(command)


def salt_delete_ip(ip, subid):
    command = 'salt "%s" cmd.run "ip addr delete %s dev eth0"' % (servers.get(subid), (ip+'/32'))
    (_, result) = commands.getstatusoutput(command)


app = Flask(__name__)


@app.route('/vps', methods=['GET', ])
def vps():
    out = []
    post = request.args.get('post')

    if post is None:
        return ''

    for lines in post.split(','):
        line = (lines.strip('\n')).split(' ')
        func = line[0]

        if func == 'list_server':
            out += list_server()
        elif func == 'list_ip':
            out += list_ip()
        elif func == 'attach_ip':
            out += attach_ip(line[1], line[2])
        elif func == 'detach_ip':
            out += detach_ip(line[1], line[2])
        elif func == 'destroy_ip':
            out += destroy_ip(line[1])
        elif func == 'create_ip':
            out += create_ip(line[1], line[2])
        else:
            out += [['--- Error Parameter ---'], ]

    return jsonify(result=out)


@app.route('/', methods=['GET', ])
def index():
    return render_template('index.html')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

