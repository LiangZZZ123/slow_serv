from sanic import Sanic
from sanic.response import json

app = Sanic("My Hello, world app")

@app.route('/', methods=['GET', 'POST'])
async def test(request):
    return json({'hello': 'world'})

if __name__ == '__main__':
    app.run(port=5000)