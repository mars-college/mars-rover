// Resize buttons and image
//
function doResize() {
  var ww;
  var wh;
  var margin = 60;
  var ratio = 320/240;
  var winportion = 0.6; // portion of vertical space taken up by image

  if (window.orientation == 90 || window.orientation == -90) {
    ww = $(window).height();
    wh = $(window).width()-margin;
  } else {
    ww = $(document).width();
    wh = $(document).height()-margin;
  }

  var iw = ww - margin*2;
  var ih = wh*winportion - margin;

  // Resize Image Stream
  if (ih * ratio > iw) {
    $("img#imagestream").height(iw/ratio);
    $("img#imagestream").width(iw);
  } else {
    $("img#imagestream").width(ih*ratio);
    $("img#imagestream").height(ih);
  }

  // Resize Table
  $("table.button").width(wh - ih);
  $("table.button").height(wh - ih);
}


$(window).load(function() {
  doResize();
  $(window).on('resize', doResize);
  $(window).on('orientationchange', doResize);
});


$(document).ready(function() {
  $("img#imagestream").attr('src', 'http://' + window.location.hostname + ':8080/?action=stream');
});


webiopi().ready(function() {
  var left, right, top, button;

  top = $( "#topbuttons" );
  left = $( "#leftbuttons" );
  right = $( "#rightbuttons" );

  webiopi().setFunction(11, "OUT"); // mode
  webiopi().digitalWrite(11, 0);    // IN-IN mode
  webiopi().setFunction(9, "OUT");  // a phase
  webiopi().setFunction(10, "OUT"); // a enable
  webiopi().setFunction(21, "OUT"); // b phase
  webiopi().setFunction(22, "OUT"); // b enable

  // Note that on iDevices, touchstart/touchend come first and
  // mousedown/mouseup are also fired, so you have to disable
  // them from within touchstart/touchend

  $("#F").bind("mousedown", function() {
    fwd();
  });
  $("#F").bind("mouseup", function() {
    stop();
  });
  $("#F").bind("touchstart", function() {
    fwd();
    $(this).unbind("mousedown");
  });
  $("#F").bind("touchend", function() {
    stop();
    $(this).unbind("mousedown");
  });

  $("#R").bind("mousedown", rev);
  $("#R").bind("mouseup", stop);
  $("#R").bind("touchstart", function() {
    rev();
    $(this).unbind("mousedown");
  });
  $("#R").bind("touchend", function() {
    stop();
    $(this).unbind("mouseup");
  });

  $("#SR").bind("mousedown", spinRight);
  $("#SR").bind("touchstart", function() {
    spinRight();
    $(this).unbind("mousedown");
  });
  $("#SR").bind("mouseup", stop);
  $("#SR").bind("touchend", function() {
    stop();
    $(this).unbind("mouseup");
  });

  $("#SL").bind("mousedown", spinLeft);
  $("#SL").bind("mouseup", stop);
  $("#SL").bind("touchstart", function() {
    spinLeft();
    $(this).unbind("mousedown");
  });
  $("#SL").bind("touchend", function() {
    stop();
    $(this).unbind("mouseup");
  });

  $("#ST").bind("mouseup", stop);
  $("#ST").bind("touchstart mousedown", stop);

  $("#ST").bind("touchstart mousedown", function() {
    stop();
    $(this).unbind("mousedown");
  });
  $("#ST").bind("touchend", function() {
    stop();
    $(this).unbind("mouseup");
  });

});

function sign(x) {
  return x / Math.abs(x);
}


function fwd() {
  webiopi().digitalWrite(11, 0);
  webiopi().digitalWrite(9, 0);  // AIN1
  webiopi().digitalWrite(21, 0); // BIN1
  webiopi().digitalWrite(10, 1); // AIN2
  webiopi().digitalWrite(22, 1); // BIN2
}

function rev() {
  webiopi().digitalWrite(11, 0);
  webiopi().digitalWrite(9, 1);	 // AIN1
  webiopi().digitalWrite(10, 0); // AIN2
  webiopi().digitalWrite(21, 1); // BIN1
  webiopi().digitalWrite(22, 0); // BIN2
}

function spinLeft() {
  webiopi().digitalWrite(11, 0);
  webiopi().digitalWrite(9, 1);	 // AIN1
  webiopi().digitalWrite(10, 0); // AIN2
  webiopi().digitalWrite(21, 0); // BIN1
  webiopi().digitalWrite(22, 1); // BIN2
}

function spinRight() {
  webiopi().digitalWrite(11, 0);
  webiopi().digitalWrite(9, 0);	 // AIN2
  webiopi().digitalWrite(10, 1); // AIN2
  webiopi().digitalWrite(21, 1); // BIN2
  webiopi().digitalWrite(22, 0); // BIN2
}

function stop() {
  webiopi().digitalWrite(11, 0);
  webiopi().digitalWrite(9, 0);	 // AIN1
  webiopi().digitalWrite(10, 0); // AIN2
  webiopi().digitalWrite(21, 0); // BIN1
  webiopi().digitalWrite(22, 0); // BIN2
}



