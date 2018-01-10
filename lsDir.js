#!/usr/bin/env node

const http = require('http');
const fs = require('fs');
const os = require('os');

const url = 'localhost';
const port = 8080;

http.createServer((request, response) => {
	writeData(response, listFiles(bashParse(request.url)));
}).listen(port, url);

function bashParse(url) {
	return os.homedir() + url.replace('~', '');
}
function listFiles(dir) {
	fs.readdir(dir, (err, files) => {
		if(err) return err.message;
		let str = '';
		files.forEach(file => {
			str += file + '\n';
		});
		return str;
	});
}
function writeData(resp, data) {
	// update later
	resp.writeHead(200, {"Content-Type": "text/plain"});
	resp.write(data);
	resp.end();
}
console.log(`server running on http://${url}/ port ${port}`);
