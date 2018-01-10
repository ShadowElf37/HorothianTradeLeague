#!/usr/bin/env node

const http = require('http');
const fs = require('fs');
const os = require('os');

const url = 'localhost';
const port = 8080;

http.createServer((request, response) => {
	listFiles(bashParse(request.url), (data) => {
		writeData(response, data);
	});
}).listen(port, url);

function bashParse(url) {
	return os.homedir() + url;
}
function listFiles(dir, callback) {
	console.log(`Listing contents of ${dir}`);
	fs.readdir(dir, (err, files) => {
		if(err) return err.message;
		let str = '';
		console.log(str + '\n');
		files.forEach(file => {
			str += file + '\n';
		});
		callback(str);
	});
}
function writeData(resp, data) {
	// update later
	resp.writeHead(200, {"Content-Type": "text/plain"});
	resp.write(data);
	resp.end();
}
console.log(`server running on http://${url}:${port}/`);
