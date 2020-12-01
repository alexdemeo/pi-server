import coffee_machine
from flask import Flask, request, Response

app = Flask(__name__)


@app.route('/coffee/<command>', defaults={'datetime': None}, methods=['PUT', 'GET'])
@app.route('/coffee/<command>/<datetime>', methods=['PUT'])
def coffee(command, datetime):
    if request.method == 'PUT' and command in ['on', 'off'] or \
            request.method == 'GET' and command == 'status':
        status_code, msg = coffee_machine.execute(command)
        return Response(response=msg, status=status_code)
    elif command == 'schedule':
        status_code, msg = coffee_machine.schedule(datetime)
        return Response(response=msg, status=status_code)
    return Response(response='Bad Request', status=400)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
