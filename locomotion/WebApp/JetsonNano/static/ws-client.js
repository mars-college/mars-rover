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
            joyUpdate =  setInterval(sendJoy, 50);
            };

        ws.onmessage = function(evt) {
            };

        ws.onclose = function(evt) {
            $("#ws-status").html("Disconnected");
            clearInterval(joyUpdate);
            clearInterval(gamepadUpdate);
            };

        // Controller

        var gamepads = {};
        var gamepadUpdate;

        function sendGamepad(){

            var gamepads = navigator.getGamepads ? navigator.getGamepads() : (navigator.webkitGetGamepads ? navigator.webkitGetGamepads : []);
            
            if ( jQuery.isEmptyObject(gamepads) ) {
                return;
            };

            var drive = deadzone(-gamepads[0].axes[1], 3);
            var turn = deadzone(gamepads[0].axes[2], 3);
                ws.send("j,"+drive+","+turn);
        }

        // zeroes out the gamepad axes and scales them using an exponential curve 
        function deadzone(value, factor) {
            const DEADZONE = 0.005;
            if (Math.abs(value) < DEADZONE) {
                value = 0.0;
            } else {                 

                if (factor != 1 && factor > 0 ){
                    if ( value < 0 ){
                        // value = -(Math.pow(factor,Math.abs(value)) - 1) / (factor-1);
                        value = -Math.pow(Math.abs(value), factor);
                    } else {
                        // value = (Math.pow(factor,value) - 1) / (factor-1);
                        value = Math.pow(value, factor);
                    }
                }
            }
            return value;
        }

        function gamepadHandler(event, connecting) {
            
            var gamepad = event.gamepad;
            // Note:
            // gamepad === navigator.getGamepads()[gamepad.index]

            if (connecting) {
                gamepads[gamepad.index] = gamepad;
                console.log("Gamepad connected at index %d: %s. %d buttons, %d axes.",
                gamepad.index, gamepad.id,
                gamepad.buttons.length, gamepad.axes.length);
                clearInterval(joyUpdate);
                gamepadUpdate = setInterval( sendGamepad, 50);
            } else {
                console.log("Gamepad disconnected from index %d: %s",
                gamepad.index, gamepad.id);
                delete gamepads[gamepad.index];
                if ( jQuery.isEmptyObject(gamepads) ){
                    clearInterval(gamepadUpdate);
                    joyUpdate = setInterval( sendJoy, 50);
                }
            }



        }

        window.addEventListener("gamepadconnected", function(e) { gamepadHandler(e, true); }, false);
        window.addEventListener("gamepaddisconnected", function(e) { gamepadHandler(e, false); }, false);


        // axes[1], = move forward/reverse
        // axes[2] = turn left/right
        // buttons[6] = decrement yaw offset by value
        // buttons[7] = increment yaw offset by value
        // buttons[4] = decrement roll offset when held
        // buttons[5] = increment roll offset when held
        // buttons[12] = increment pitch offset when held
        // buttons[13] = decrement pitch offset when held
        // buttons[0] = clear ypr offsets
        // buttons[2] = clear yaw offsets
        // buttons[3] = clear pitch offsets
        // buttons[1] = clear roll offsets
        

        // Joystick Element

        // Create JoyStick object into the DIV 'joy1Div'
        var Joy1 = new JoyStick('joy1Div');
        var joyUpdate;

        var joy1IinputPosX = document.getElementById("joy1PosX");
        var joy1InputPosY = document.getElementById("joy1PosY");
        var joy1Dir = document.getElementById("joy1Dir");
        var joy1X = document.getElementById("joy1X");
        var joy1Y = document.getElementById("joy1Y");

        function sendJoy(){
            ws.send("j,"+Joy1.GetY()+","+Joy1.GetX());
            joy1IinputPosX.value=Joy1.GetPosX();
            joy1InputPosY.value=Joy1.GetPosY();
            joy1Dir.value=Joy1.GetDir();
            joy1X.value=Joy1.GetX();
            joy1Y.value=Joy1.GetY();
        }

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
