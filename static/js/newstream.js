function updateNumCharsAllowed(numChars){
	$("#charsTotal").text(numChars);
	$("#charsLeft").text(numChars);
	$("#tweet-textarea").attr('maxlength', numChars);
}

function showOnlyMyTweets(){
	$(".tweet-tile").each(function(index){
		author_class = $(this).attr('class').split(" ")[0];
		if(author_class == "False"){
			$(this).hide();
		}
	});
	show_only_my_tweets = true
}

function showAllTweets(){
	$(".tweet-tile").each(function(index){
		$(this).show();
	});
	show_only_my_tweets = false
}

function addClickability() {
	$(".tweet-tile-interior").click(function(){
		$("#"+focused_thread).removeClass("active-thread");
		$(this).addClass("active-thread");
		focused_thread = $(this).attr('id');
		hashtag_to_track = $("#hashtagToTrack-js").text().trim();
		thought_hashtag = $(".sidebar-content-js").attr('id');
		full_hashtag_text = " #"+thought_hashtag + " #"+hashtag_to_track;
		$(".chars").text(140 - full_hashtag_text.length);
		focused_data = $.parseJSON($(this).children('input').val());
		$.ajax({
			  type: "POST",
			  contentType: "application/json; charset=utf-8",
			  url: "/focus",
			  data: JSON.stringify(focused_data)
			}).done(function(focusHtml){
				$('#sidebar-content-js').html(focusHtml);
			})
	});
}

$( document ).ready(function() {
	show_only_my_tweets = false;
	focused_thread = $(".tweet-tile-interior:first").attr('id');
	addClickability();
	$(".tweet-tile-interior:first").addClass("active-thread");
	
	$("#sort-my-thoughts-button").click(function(){
		showOnlyMyTweets();
		$(this).addClass("toggle-clicked");
		$("#sort-most-recent-button").removeClass("toggle-clicked");
	});
	
	$("#sort-most-recent-button").click(function(){
		showAllTweets();
		$(this).addClass("toggle-clicked");
		$("#sort-my-thoughts-button").removeClass("toggle-clicked");
	});

	$("#new-thread-button").click(function(){
		$("#sidebar-content-js").toggle();
		$("#newThread").toggle();
		if ($("#new-group-name").is(':visible')==true) {
			new_thread = true;
			$("#"+ focused_thread).removeClass("thought-tile-selected");
			updateNumCharsAllowed(106);
		}
		else{
			new_thread = false;
			$("#"+ focused_thread).addClass("thought-tile-selected");
			var numCharsUsed = 140-(" #" + focused_thread + " #classtweeter").length;
			updateNumCharsAllowed(numCharsUsed);
		}
	});
	$('#tweet-textarea').bind('input propertychange', function() {
		numCharsTotal = parseInt($('#charsTotal').text())
		numCharsInput = $('#tweet-textarea').val().length;
		$('#charsLeft').text((numCharsTotal - numCharsInput).toString()) //HA-->somehow this gets refreshed back to updateNumCharsAllowed(numCharsUsed); every 5 seconds?
	})
	$("#send-tweet-button").click(function(){
		text = $('#tweet-textarea').val();
		console.log("clicked");
		if (text.length > 0){
			additional_hashtags = " #" + focused_thread + " #classtweeter"
			if ($("#new-group-name").is(':visible')==true) {
				additional_hashtags = " #" + $("#new-group-name").val().toLowerCase().split(" ").join("_") + " #classtweeter";
			}
			composed_tweet = text + additional_hashtags;
			$.post( "/sendToTwitter", composed_tweet, function(data){
				$('#tweet-textarea').val("");
				$("#send-tweet-button").removeClass("btn-unsent").addClass("btn-sent");
				$("#send-tweet-button").text("SENT!");
				$("#new-thread-form-group").removeClass("has-error");
				$("#new-thread-control-label").text("New Thread Name");
				if ($("#new-group-name").is(':visible')==true) {
					$("#sidebar-content-js").toggle();
					$("#newThread").toggle();
					$("#"+focused_thread).addClass("thought-tile-selected");
					var numCharsUsed = 140-(" #" + focused_thread + " #classtweeter").length;
					updateNumCharsAllowed(numCharsUsed);
				}
				setTimeout(function() { $("#send-tweet-button").removeClass("btn-sent").addClass("btn-unsent"); $("#send-tweet-button").text("Send");}, 3000)
			})
		}
		else{
			$("#new-thread-form-group").addClass("has-error");
			$("#new-thread-control-label").text("You must name the thread...");
		}
		
	})

	window.setInterval(function(){
		$.get( "/refresh", function( tweetHtml ) {
			console.log("refreshed");
			$("#tweetcard-js").html(tweetHtml);
			addClickability();
			$("#"+focused_thread).addClass("active-thread");
			$.get( "/refresh_sidebar?focused_group="+focused_thread, function( sidebarHtml ) {
				$("#sidebar-content-js").html(sidebarHtml);
			})
		});
		
	}, 5000);
});



