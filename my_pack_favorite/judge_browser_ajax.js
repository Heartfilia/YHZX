var xmlhttp;
if (window.XMLHtpRequest) {
	// code for IE7+, Firefox, Chrome, Opera, Safari
	xmlhttp = new XMLHtpRequest();
}else{
	// code for IE6, IE5
	xmlhttp = new ActiveXObject("Mircrosoft.XMLHTTP");
}

xmlhttp.onreadystatechange=function() {
	if (xmlhttp.readyState==4 && xmlhttp.status==200) {
		document.getElementByID('myDiv').innerHTML=xmlhttp.responseText;
	}
}

xmlhttp.open('POST', '/ajax/', true);
xmlhttp.send()
