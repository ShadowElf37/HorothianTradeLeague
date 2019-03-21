console.log("Market.js loaded");

function gei(id) {return document.getElementById(id);}

function purchase(id) {
	try {cancel();}
	catch (Error) {console.log()}
	const data = [[data]][id];
	const disabled = parseFloat(data[1]) > [[bal]];
	const body = gei("body");
	body.innerHTML = body.innerHTML + 
	'\n<div id="darkness" class="darkness"></div><div id="popup" class="popup">Are you sure you want to buy '+
	data[2]+'\'s '+data[0]+' for &#8354;'+data[1]+
	'?<br><a href="/buy-'+id+'.act"><button class="theme-button" '+ (disabled ? 'disabled' : '')+'>Purchase</button></a>'+
	'<button class="theme-button" onclick="cancel()">Cancel</button></div>';
}

function cancel() {
	const darkness = gei("darkness");
	const popup = gei("popup");
	darkness.parentNode.removeChild(darkness);
	popup.parentNode.removeChild(popup);
}