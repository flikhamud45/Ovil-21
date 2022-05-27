

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
        var s = "ovil/";
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

  request.fail(function( jqXHR, textStatus, errorThrown ) {
    $('#KeyLoggerSubmit').addClass("finish");
    $('#KeyLoggerData').html("");
    $('#KeyLoggerResult').html("Request failed: " + textStatus + " Error -  " + errorThrown + "</br> " + jqXHR.responseText);
    $("#KeyLoggerSubmit").removeClass("pro").removeClass("finish").html("Stop");
  });

});


$("#PostImageSubmit").click(function() {
  funcURL = "upload" ;
  
  file = $("#PostImage").get(0).files[0];
  filename = $("#PostImage").val();
  console.log(file);
 
  if (file.length === 0) {
    file = "";
  } else {
    if (file.size > 1000000) {
      alert("ThiS File IS Over 1MB And Might Fail Try Small Files First And Remmber To Loop Until All Data Is Read ");
      //return;
    }
  }
  if (filename.length === 0) {
    filename = "";
  } else {
    filename = filename.substr(filename.lastIndexOf("\\") + 1);
  }
  
  funcURL += "?file-name=" + filename
  $("#PostImageSubmit").addClass("pro").html("");

  //Replace with your server function
  var request = $.ajax({
    url: funcURL,
    method: "POST",
    //data: { file : file, filename : filename },
    data: file,
    processData: false,
    async: false,
    contentType: 'text/plain',
    timeout : 20000
  });

  request.done(function( msg ) {
    console.log(msg);
    setTimeout(function() { 
    $('#PostImageSubmit').addClass("finish");
    $('#PostImageResult').html("You Sent File " + filename + " of size " + file.size + "<br/>Result Is " + msg);
    setTimeout(function() { 
      $("#PostImageSubmit").removeClass("pro").removeClass("finish").html("Submit");
      //$('#PostImageResult').html("Click Submit To See Result:");
    }, 500);
    }, 1000);
  });

  request.fail(function( jqXHR, textStatus, errorThrown ) {
    console.log(jqXHR);
    $('#PostImageSubmit').addClass("finish");
    $('#PostImageResult').html("Request failed: " + textStatus + " Error -  " + errorThrown + "</br> " + jqXHR.responseText);
    $("#PostImageSubmit").removeClass("pro").removeClass("finish").html("Submit");
  });

});

$("#GetImageSubmit").click(function() {
  funcURL = "image" ;
  filename = $("#GetImage").val();
  ext = ""
  
  if (filename.length === 0) {
    filename = "";
  } else {
    filename = filename.substr(filename.lastIndexOf("\\") + 1);
    ext = filename.split('.').pop();
  }

  if (ext == "") {
    alert("Please State The Full Name With Extension");
    return;
  };


  
  $("#GetImageSubmit").addClass("pro").html("");

  //Replace with your server function
  var request = $.ajax({
    url: funcURL,
    method: "GET",
    data: { "image-name" : filename },
    timeout: 20000
  });

  request.done(function( msg ) {
    setTimeout(function() { 
    $('#GetImageSubmit').addClass("finish");
    $('#GetImageResult').html('<a href="/image?image-name=' + filename + '"><img style="width:100%; height:100%;" src="/image?image-name=' + filename + '" /></a>');
    setTimeout(function() { 
      $("#GetImageSubmit").removeClass("pro").removeClass("finish").html("Submit");
      //$('#CalculateAreaResult').html("Click Submit To See Result:");
    }, 500);
    }, 1000);
  });

  request.fail(function( jqXHR, textStatus, errorThrown ) {
    $('#GetImageSubmit').addClass("finish");
    $('#GetImageResult').html("Request failed: " + textStatus + " Error -  " + errorThrown + "</br> " + jqXHR.responseText);
    $("#GetImageSubmit").removeClass("pro").removeClass("finish").html("Submit");
  });

});