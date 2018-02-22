// Stolen from W3Schools
function getCookie(cname) {
    var name = cname + "=";
    var decodedCookie = decodeURIComponent(document.cookie);
    var ca = decodedCookie.split(';');
    for(var i = 0; i <ca.length; i++) {
        var c = ca[i];
        while (c.charAt(0) == ' ') {
            c = c.substring(1);
        }
        if (c.indexOf(name) == 0) {
            return c.substring(name.length, c.length);
        }
    }
    return "";
}


function updateMessage(id, caller) {
	if (caller.innerHTML.slice(1, 7) != "button"){
		document.getElementById("msg-body").textContent = "Loading...";

		fetch("http://localhost:8080/m/" + id).then(function(response) {
			response.text().then(function(text) {
				document.getElementById("msg-body").innerHTML = text;
			});
		});
		console.log('Pulled contents of message ' + id);

		caller.innerHTML = '<button onclick="deleteMessage(\''+id+'\')" class="delete-button"></button>\n' + caller.innerHTML;
	}
}


function mouseLeave(caller) {
	caller.innerHTML = caller.innerHTML.split("\n").slice(1).join("\n");
	//console.log(getCookie('client-id'))
}


function deleteMessage(id){
	document.getElementById("msg-body").textContent = "No message selected.";
	var elem = document.getElementById(id);
	var parent = elem.parentNode
	parent.removeChild(elem);

	//console.log(getCookie('client-id'))

	fetch("http://localhost:8080/del_msg.act/" + id + '/' + getCookie('client-id')).then(function(response) {
		response.text().then(function(text) {});
	});

	if (parent.innerHTML == ""){
		parent.innerHTML = '<span class="no-message">Inbox empty...</span>'
	}
}