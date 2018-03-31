function confirmRedirect(link){
	if (confirm("Are you sure you want to do that?") == true) {
		window.location.href = link;
	}
}