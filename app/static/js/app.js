var publisher;
var targetElement = 'publisher';
// var subscriber;
var session;
var publisherName = $('#publisher').data('publisher_name');
var subscriberName
var apiKey = window.main_secret
var sessionId = window.sessionId
var token = window.token
var call_pin = window.call_pin

initializeSession();

// Handling all of our errors here by alerting them
function handleError(error) {
  if (error) {
    alert(error.message);
  }
}



function initializeSession() {
  session = OT.initSession(apiKey, sessionId);

  // Create a publisher
  publisher = OT.initPublisher('publisher', {
    insertMode: 'append',
    width: '100%',
    height: '100%',
    name: publisherName,
    // showControls: false,
    style: {buttonDisplayMode: 'off', audioLevelDisplayMode: 'off',}
  }, handleError);

  publisherDom = document.getElementById('publisher');
  publisherDom.insertAdjacentHTML( 'beforeend', '<div id="muted_or"><i class="bi bi-mic-fill"></i></div>' );
  // Subscribe to a newly created stream
  session.on('streamCreated', function(event) {
    // console.log(event.stream.hasAudio)
    var stream = event.stream
	  var subscriber = session.subscribe(event.stream, 'subscriber', {
	    insertMode: 'append',
	    width: '100%',
	    height: '100%',
      style: {buttonDisplayMode: 'off', nameDisplayMode: "off"}
	  }, function(error){
      if (error) {
        console.log(error.message)
        return;
      }
      if(document.getElementById('no_one')){
        document.getElementById('no_one').remove();
      }

      subscriberName = subscriber.stream.name
      const domElement = document.getElementById(subscriber.id);
      domElement.classList.add('per-sub')
      domElement.insertAdjacentHTML( 'beforeend', '<p id="sub_name">' + subscriberName + '</p>' );

      // domElement.style.width = '500px';
      // domElement.style.height = 'auto';

      if (subscriber.stream.hasAudio) {
        // console.log('hasAudio')
        domElement.insertAdjacentHTML( 'beforeend', '<div id="muted_or"><i class="bi bi-mic-fill"></i></div>' );
      }else{
        domElement.insertAdjacentHTML( 'beforeend', '<div id="muted_or"><i class="bi bi-mic-mute-fill"></i></div>' );
      }

      if (subscriber.stream.hasVideo) {
        var imgData = subscriber.getImgData();
        subscriber.setStyle('backgroundImageURI', imgData);
      } else {
        if(domElement.querySelector('#videoOff')){
          domElement.removeChild(domElement.querySelector('#videoOff'))
        }
        domElement.insertAdjacentHTML( 'beforeend', '<div id="videoOff"><h1>' + subscriber.stream.name.charAt(0).toUpperCase() + '</h1></div>' );
        subscriber.setStyle('backgroundImageURI',
          ''
        );
      }
      var subLength = $('#subscriber').find('.per-sub').length
      
      if(subLength > 8){
        $('#subscriber').find('.per-sub').css('width', '250px');
        $('#subscriber').find('.per-sub').css('height', 'auto');
      }else if(subLength > 6){
        $('#subscriber').find('.per-sub').css('width', '350px');
        $('#subscriber').find('.per-sub').css('height', 'auto');
      }else if(subLength > 2){
        $('#subscriber').find('.per-sub').css('width', '500px');
        $('#subscriber').find('.per-sub').css('height', 'auto');
      }else if(subLength = 2){
        $('#subscriber').find('.per-sub').css('width', '50%');
      }
    });

    console.log($('#subscriber').find('.per-sub').length)

    session.on('connectionDestroyed', function(event){
      if($('#subscriber').find('.per-sub').length){
        // console.log('hello')
        // console.log($('#subscriber').find('.per-sub').length)
      }else{
        if(!document.getElementById('no_one')){
          var noOneDiv = document.createElement("div");
          noOneDiv.id = 'no_one';
          noOneDiv.innerHTML = '<h1>Please wait until someone join the meeting.</h1>';
          document.getElementById('subscriber').appendChild(noOneDiv)
        }
        
      }
    })
    // console.log($('#subscriber').find('.per-sub').length)

    session.on('streamPropertyChanged', function(event){
      domElement = document.getElementById(subscriber.id);
      publisherDom = document.getElementById(publisher.id);

      if(domElement){
        if(domElement.querySelector('#muted_or')){
          domElement.removeChild(domElement.querySelector('#muted_or'))
        }

        if(subscriber.stream.hasAudio){
          domElement.insertAdjacentHTML( 'beforeend', '<div id="muted_or"><i class="bi bi-mic-fill"></i></div>' );
        }else{
          domElement.insertAdjacentHTML( 'beforeend', '<div id="muted_or"><i class="bi bi-mic-mute-fill"></i></div>' );
        }

        if(domElement.querySelector('#videoOff')){
          domElement.removeChild(domElement.querySelector('#videoOff'))
        }

        if(subscriber.stream.hasVideo){
          //console.log('has video')
        }else{
          subscriber.setStyle('backgroundImageURI',
            ''
          );
          domElement.insertAdjacentHTML( 'beforeend', '<div id="videoOff"><h1>' + subscriber.stream.name.charAt(0).toUpperCase() + '</h1></div>' );
        }
      }

    })


	});

  // Connect to the session
  session.connect(token, function(error) {
    // If the connection is successful, publish to the session
    if (error) {
      handleError(error);
    } else {
      session.publish(publisher, handleError);
    }
  });

  ////////////////////////////
  var msgHistory = document.querySelector('#history_box');
  var currentConnectionId
  session.on('signal:msg', function signalCallback(event) {
    var msgDiv = document.createElement('div');
    msgDiv.className = event.from.connectionId === session.connection.connectionId ? 'mine' : 'theirs';
    msgDiv.setAttribute("id", event.from.connectionId)
    var msg = document.createElement('p');
    var msgUser = document.createElement('p');
    msg.textContent = event.data;
    msg.className = 'msg-content'
    msgUser.textContent = msgDiv.className === 'mine' ? publisherName : subscriberName
    msgUser.className = 'msg-user'

    if($('#history_box').children().length > 0){
      // console.log($('#history_box').children().last().attr("id"));
      if($('#history_box').children().last().attr("id") == event.from.connectionId){
        $('#history_box').children().last().append(msg)
      }else{
        msgDiv.appendChild(msgUser)
        msgDiv.appendChild(msg)
        msgHistory.appendChild(msgDiv);
      }
    }else{
      msgDiv.appendChild(msgUser)
      msgDiv.appendChild(msg)
      msgHistory.appendChild(msgDiv);
    }
    
    // msg.scrollIntoView();
  });
}



// Text chat
var form = document.querySelector('#message_form');
var msgTxt = document.querySelector('#messages');

// Send a signal once the user enters data in the form
form.addEventListener('submit', function submit(event) {
  event.preventDefault();

  session.signal({
    type: 'msg',
    data: msgTxt.value
  }, function signalCallback(error) {
    if (error) {
      console.error('Error sending signal:', error.name, error.message);
    } else {
      msgTxt.value = '';
    }
  });
});
///////////////////////////////

$("#call_disconnect").click(function(e) {
  session.disconnect(publisher)
  window.location.href = window.location.protocol+ '//' + window.location.host + '/optok';
})

$("#message").click(function(){
  const videos = document.querySelector('#videos')
  const messageBox = document.querySelector('#message_box')
  videos.classList.toggle('collapse_message_box')
  messageBox.classList.toggle('collapse_message_box')
});

function videoMute() {
  const div = document.getElementById('publisher');
  const videoMute = document.getElementById('videomute');
  publisherDom = document.getElementById(publisher.id)
  div.classList.toggle('offVideo');
  if(div.classList.contains('offVideo')){
    publisher.publishVideo(false);
    videoMute.style.color = 'black'
    videoMute.style.backgroundColor = 'white'
    videoMute.innerHTML = '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-camera-video-off-fill" viewBox="0 0 16 16"><path fill-rule="evenodd" d="M10.961 12.365a1.99 1.99 0 0 0 .522-1.103l3.11 1.382A1 1 0 0 0 16 11.731V4.269a1 1 0 0 0-1.406-.913l-3.111 1.382A2 2 0 0 0 9.5 3H4.272l6.69 9.365zm-10.114-9A2.001 2.001 0 0 0 0 5v6a2 2 0 0 0 2 2h5.728L.847 3.366zm9.746 11.925-10-14 .814-.58 10 14-.814.58z"/></svg>'
    publisher.setStyle('backgroundImageURI','');
    publisherDom.insertAdjacentHTML( 'beforeend', '<div id="videoOff"><h1>' + publisherName.charAt(0).toUpperCase() + '</h1></div>' );
  }else{

    if(publisherDom.querySelector('#videoOff')){
      publisherDom.removeChild(publisherDom.querySelector('#videoOff'))
    }

    publisher.publishVideo(true);
    videoMute.style.color = 'white'
    videoMute.style.backgroundColor = 'gray'
    videoMute.innerHTML = '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-camera-video-fill" viewBox="0 0 16 16"><path fill-rule="evenodd" d="M0 5a2 2 0 0 1 2-2h7.5a2 2 0 0 1 1.983 1.738l3.11-1.382A1 1 0 0 1 16 4.269v7.462a1 1 0 0 1-1.406.913l-3.111-1.382A2 2 0 0 1 9.5 13H2a2 2 0 0 1-2-2V5z"/></svg>'
  }
}

function audioMute() {
  const div = document.getElementById('publisher');
  if(div.querySelector('#muted_or')){
    div.removeChild(div.querySelector('#muted_or'))
  }
  const muteButton = document.getElementById('audiomute');
  div.classList.toggle('offAudio');
  if(div.classList.contains('offAudio')){
    publisher.publishAudio(false);
    muteButton.style.color = 'black'
    muteButton.style.backgroundColor = 'white'
    muteButton.innerHTML = '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-mic-mute-fill" viewBox="0 0 16 16"><path d="M13 8c0 .564-.094 1.107-.266 1.613l-.814-.814A4.02 4.02 0 0 0 12 8V7a.5.5 0 0 1 1 0v1zm-5 4c.818 0 1.578-.245 2.212-.667l.718.719a4.973 4.973 0 0 1-2.43.923V15h3a.5.5 0 0 1 0 1h-7a.5.5 0 0 1 0-1h3v-2.025A5 5 0 0 1 3 8V7a.5.5 0 0 1 1 0v1a4 4 0 0 0 4 4zm3-9v4.879L5.158 2.037A3.001 3.001 0 0 1 11 3z"/><path d="M9.486 10.607 5 6.12V8a3 3 0 0 0 4.486 2.607zm-7.84-9.253 12 12 .708-.708-12-12-.708.708z"/></svg>'
    div.insertAdjacentHTML( 'beforeend', '<div id="muted_or"><i class="bi bi-mic-mute-fill"></i></div>' );
  }else{
    publisher.publishAudio(true);
    muteButton.style.color = 'white'
    muteButton.style.backgroundColor = 'gray'
    muteButton.innerHTML = '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-mic-fill" viewBox="0 0 16 16"><path d="M5 3a3 3 0 0 1 6 0v5a3 3 0 0 1-6 0V3z"/><path d="M3.5 6.5A.5.5 0 0 1 4 7v1a4 4 0 0 0 8 0V7a.5.5 0 0 1 1 0v1a5 5 0 0 1-4.5 4.975V15h3a.5.5 0 0 1 0 1h-7a.5.5 0 0 1 0-1h3v-2.025A5 5 0 0 1 3 8V7a.5.5 0 0 1 .5-.5z"/></svg>'
    div.insertAdjacentHTML( 'beforeend', '<div id="muted_or"><i class="bi bi-mic-fill"></i></div>' );
  }
}

$('#options').click(function(){
  $("#option_popup").toggle();
})

$('#copy_link_button').click(function(){
  callUrl = $('#copy_join_link').html()
  copyClipboard(callUrl)
})

$('#copy_message_button').click(function(){
  callUrl = 'To join the video meeting, click this link: ' + $('#copy_join_link').html() + ' Use pin: ' + call_pin;
  copyClipboard(callUrl)
})

function copyClipboard(text){
  var $temp = $("<input>");
  $("body").append($temp);
  $temp.val(text).select();
  document.execCommand("copy");
  $temp.remove();
}
