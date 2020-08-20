
http = require('http')

const requestListener = (req, res) => {
    let body = ""
    req.on('data', chunk => {
        body += chunk
    })

    req.on('end', () => {

        console.log("POST data:")
        console.log(body)

        res.writeHead(200);
        res.end('Hello, World!');
    })
}

const server = http.createServer(requestListener);
server.listen(8080);
