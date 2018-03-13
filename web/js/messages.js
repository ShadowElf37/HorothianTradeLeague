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

// Stolen from stackoverflow
function getPosition(str, m, i) { return str.split(m, i).join(m).length; }

var messages = {}; // this is easy to render; instant loading is possible

// This will update the message text and fetch from server
function updateMessage(id, caller) {
	if (caller.innerHTML.slice(1, 7) != "button"){
		document.getElementById("msg-body").textContent = "Loading...";

        if (id in messages){
            document.getElementById("msg-body").innerHTML = messages[id];
        }
		else {fetch("http://[[host]]:[[port]]/m/" + id).then(function(response) {
                response.text().then(function(text) {
                    body = document.getElementById("msg-body")

                    console.log(text);
                    while (text.search('&#x7B;') != -1) {
                        i0 = text.search('&#x7B;');
                        i1 = text.search('&#x7D;');
                        s = text.slice(i0+6, i1);
                        s = s.split('&#x7C;');
                        console.log(s)
                        text = text.replace(text.slice(i0, i1+6), "<a target=\"blank\" href=\""+s[1]+"\">"+s[0]+"</a>");
                    }

                    while (text.search('\\*') != -1) {
                        i0 = getPosition(text, '*', 1);
                        i1 = getPosition(text, '*', 2);
                        s = text.slice(i0+1, i1);
                        text = text.replace(text.slice(i0, i1+1), "<strong>"+s+"</strong>");
                    }

                    body.innerHTML = text;
                    messages[id] = text;
                });
            });
		};
		console.log('Pulled contents of message ' + id);

		caller.innerHTML = '<button onclick="deleteMessage(\''+id+'\')" class="delete-button"></button>\n' + caller.innerHTML;
	}
}


// Just removes trash can icon
function mouseLeave(caller) {
	caller.innerHTML = caller.innerHTML.split("\n").slice(1).join("\n");
}

// Tells server to delete message
function deleteMessage(id){
	var elem = document.getElementById(id);
	var parent = elem.parentNode
	parent.removeChild(elem);

	fetch("http://[[host]]:[[port]]/del_msg.act/" + id + '/' + getCookie('client-id')).then(function(response) {
		response.text().then(function(text) {});
	});

	if (parent.innerHTML.trim() == ""){
		parent.innerHTML = '<span class="no-message">Inbox empty...</span>'
	}
    document.getElementById("msg-body").textContent = "No message selected.";
}