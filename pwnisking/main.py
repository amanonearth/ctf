from flask import Flask, render_template, request, redirect, url_for, flash, make_response
import hashlib
import subprocess
import socket

app = Flask(__name__)
app.config['SECRET_KEY'] = "just-one-m0re-CTF"

started = False
status = ""
value = ""
userflag = False
rootflag = False
resetonce = False
first = None

@app.route('/', methods=['GET', 'POST'])
def index():
    global started
    global status
    global value
    if request.method == 'GET':
        status = "Not Active"
        value = "Start Machine"
        return render_template('index.html', status=status, value=value)
    elif request.method == "POST":
        if not started:
            started = True
            subprocess.call(["bash", "build.sh"])
        if started:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip_add = s.getsockname()[0]
            # print(ip_add)
            value = "IP: " + str(ip_add)
            flash(" Machine Started Successfully")
            status = "Active"
            # flash("In case you are facing an issue with the machine, You can reset it anytime from /reset")
            resetinfo = "In case you are facing an issue with the machine, You can reset it anytime from /reset"
        return render_template('index.html', status=status, value=value, resetinfo=resetinfo)
    else:
        return render_template('index.html')

@app.route('/reset', methods=['GET', 'POST'])
def reset():
    global status
    global value
    global resetonce
    if request.method == "GET":
        value1 = "Reset"
        return render_template('reset.html', status=status, value=value, value1=value1)
    elif request.method == "POST":
        if not resetonce:
            resetonce = True
            global userflag
            global rootflag
            userflag = False
            rootflag = False
            subprocess.call(["docker", "stop", "pwnisking-container"])
            subprocess.call(["bash", "build.sh"])
        if resetonce:
            value1 = "Reset Success"
            return render_template('reset.html', status=status, value=value, value1=value1)
    else:
        value1 = ""
        return render_template('reset.html', status=status, value=value, value1=value1)


@app.route('/flag', methods=['GET', 'POST'])
def gfgd():
    global userflag
    global rootflag
    global first
    if request.method == 'GET':
        value1 = "Submit"
        return render_template('flag.html', value1=value1)
    elif request.method == "POST":
        flagu = request.form['flagu']
        flago = hashlib.md5(flagu.encode())
        if flago.hexdigest() == "1205a61c9ff8816a20267ecbc008a447" or flago.hexdigest() == "8360fb3f9f8077804bc41d3792f77386":
            if flago.hexdigest() == "1205a61c9ff8816a20267ecbc008a447":
                userflag = True
                if first != "root":
                    first = "user"
            elif flago.hexdigest() == "8360fb3f9f8077804bc41d3792f77386":
                rootflag = True
                if first != "user":
                    first = "root"
            if userflag and rootflag:
                subprocess.call(["docker", "stop", "pwnisking-container"])
                global status
                global value
                global started
                started = False
                status = "Not Active"
                value = "Start Machine"
                if first == "user":
                    flash('Congratulation! Your root flag is correct.')
                elif first == "root":
                    flash('Congratulation! Your user flag is correct.')
                flash('Machine Terminated')
                userflag = False
                rootflag = False
                first = None
                return render_template('index.html', status=status, value=value)
            if userflag:
                flash('Congratulation! Your user flag is correct.')
                return render_template('index.html', status=status, value=value)
            if rootflag:
                flash('Congratulation! Your root flag is correct.')
                return render_template('index.html', status=status, value=value)

        else:
            value1 = "You provided the wrong flag"
            return render_template('flag.html', value1=value1)
    else:
        value = "Submit"
        return render_template('flag.html', value=value)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8000)
