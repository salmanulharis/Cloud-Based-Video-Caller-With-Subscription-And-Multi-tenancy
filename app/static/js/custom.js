$('#copy_url').click(function(){
	callUrl = $('#join_link').html()
	var $temp = $("<input>");
	$("body").append($temp);
	$temp.val(callUrl).select();
	document.execCommand("copy");
	$temp.remove();
})