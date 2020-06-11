$(document).ready(function(){

        // Websocket

        var WEBSOCKET_ROUTE = "/ws";
        var ws = null;

        if(window.location.protocol == "http:"){
            //localhost
            ws = new WebSocket("ws://" + window.location.host + WEBSOCKET_ROUTE);
            }
        else if(window.location.protocol == "https:"){
            //Dataplicity
            ws = new WebSocket("wss://" + window.location.host + WEBSOCKET_ROUTE);
            }

        ws.onopen = function(evt) {
            $("#ws-status").html("Connected");
            };

        ws.onmessage = function(evt) {
            };

        ws.onclose = function(evt) {
            $("#ws-status").html("Disconnected");
            };

        // Joystick Element

        // Create JoyStick object into the DIV 'joy1Div'
        var Joy1 = new JoyStick('joy1Div');

        var joy1IinputPosX = document.getElementById("joy1PosX");
        var joy1InputPosY = document.getElementById("joy1PosY");
        var joy1Dir = document.getElementById("joy1Dir");
        var joy1X = document.getElementById("joy1X");
        var joy1Y = document.getElementById("joy1Y");

        setInterval(
            function(){
                ws.send("j,"+Joy1.GetY()+","+Joy1.GetX());
                joy1IinputPosX.value=Joy1.GetPosX();
                joy1InputPosY.value=Joy1.GetPosY();
                joy1Dir.value=Joy1.GetDir();
                joy1X.value=Joy1.GetX();
                joy1Y.value=Joy1.GetY();
                }, 50);

        // Buttons

        $("#green_on").click(function(){
            ws.send("on_g");
            });

        $("#green_off").click(function(){
            ws.send("off_g");
            });

        $("#red_on").click(function(){
            ws.send("on_r");
            });

        $("#red_off").click(function(){
            ws.send("off_r");
            });

    	$("#blue_on").click(function(){
                ws.send("on_b");
                });

        $("#blue_off").click(function(){
            ws.send("off_b");
            });

    	$("#white_on").click(function(){
                ws.send("on_w");
                });

        $("#white_off").click(function(){
            ws.send("off_w");
            });


      });
