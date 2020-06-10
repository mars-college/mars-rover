/*
   Copyright 2012 Eric Ptak - trouch.com

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
*/

var _gaq = _gaq || [];
var _webiopi;

function w() {
	if (_webiopi == undefined) {
		_webiopi = new WebIOPi();
	}
	
	return _webiopi;
}

function webiopi() {
	return w();
}

function WebIOPi() {
	this.context = "/";
	this.GPIO = Array(54);
	this.PINS = Array(27);

	this.TYPE = {
			DNC: {value: 0, style: "DNC", label: "--"},
			GND: {value: 1, style: "GND", label: "GROUND"},
			V33: {value: 2, style: "V33", label: "3.3V"},
			V50: {value: 3, style: "V50", label: "5.0V"},
			GPIO: {value: 4, style: "GPIO", label: "GPIO"}
	};
	
	this.ALT = {
			I2C0: {name: "I2C0", enabled: false, gpios: []},
			I2C1: {name: "I2C1", enabled: false, gpios: []},
			SPI0: {name: "SPI0", enabled: false, gpios: []},
			UART0: {name: "UART0", enabled: false, gpios: []}
		};
		
	// init GPIOs
	for (var i=0; i<this.GPIO.length; i++) {
		var gpio = Object();
		gpio.value = 0;
		gpio.func = "IN";
		gpio.mapped = false;
		this.GPIO[i] = gpio;
	}

	// get context
	var scripts = document.getElementsByTagName("script");
	//var styles = document.getElementsByTagName("link");

	var reg = new RegExp("http://" + window.location.host + "(.*)webiopi.js");
	for(var i = 0; i < scripts.length; i++) {
		var res = reg.exec(scripts[i].src);
		if (res && (res.length > 1)) {
			script = scripts[i];
			this.context = res[1];
			
		}
	}

	var head = document.getElementsByTagName('head')[0];

	var style = document.createElement('link');
	style.rel = "stylesheet";
	style.type = 'text/css';
	style.href = './webiopi.css';
	head.insertBefore(style, scripts[0]);
	
	var jquery = document.createElement('script');
	jquery.type = 'text/javascript';
	jquery.src = './jquery.js';
	jquery.onload = function() {
		w().init();
	};
	jquery.onreadystatechange = function() {
		if (this.readyState == 'complete') {
			w().init();
		}
	};
	head.insertBefore(jquery, scripts[0]);
	
	// GA
	// _gaq.push(['_setAccount', 'UA-33979593-2']);
	// _gaq.push(['_trackPageview']);
		
	// var ga = document.createElement('script');
	// ga.type = 'text/javascript';
	// ga.async = false;
	// ga.src = ('https:' == document.location.protocol ? 'https://ssl' : 'http://www') + '.google-analytics.com/ga.js';
	// head.insertBefore(ga, scripts[0]);
	
	// init ALTs
	this.addALT(this.ALT.I2C0, 0, "SDA");
	this.addALT(this.ALT.I2C0, 1, "SCL");

	this.addALT(this.ALT.I2C1, 2, "SDA");
	this.addALT(this.ALT.I2C1, 3, "SCL");

	this.addALT(this.ALT.SPI0,  7, "CE1");
	this.addALT(this.ALT.SPI0,  8, "CE0");
	this.addALT(this.ALT.SPI0,  9, "MISO");
	this.addALT(this.ALT.SPI0, 10, "MOSI");
	this.addALT(this.ALT.SPI0, 11, "SCLK");
	
	this.addALT(this.ALT.UART0, 14, "TX");
	this.addALT(this.ALT.UART0, 15, "RX");
	
}

WebIOPi.prototype.init = function() {
	$.getJSON(w().context + "map", function(data) {
		var count = w().PINS.length;
		for (i = 0; i<count-1; i++) {
			var type = w().TYPE.GPIO;
			var label = data[i];
			
			if (label == "DNC") {
				type = w().TYPE.DNC;
			}
			else if (label == "GND") {
				type = w().TYPE.GND;
			}
			else if (label == "V33") {
				type = w().TYPE.V33;
			}
			else if (label == "V50") {
				type = w().TYPE.V50;
			}
			
			if (type.value != w().TYPE.GPIO.value) {
				label = type.label;
			}
			
			w().map(i+1, type, label);
		}
		if (w().readyCallback != undefined) {
			w().readyCallback();
		}
		w().updateUI();
		w().checkVersion();
	});
}


WebIOPi.prototype.ready = function (cb) {
	w().readyCallback = cb;
}

WebIOPi.prototype.map = function (pin, type, value) {
	w().PINS[pin] = Object();
	w().PINS[pin].type = type
	w().PINS[pin].value = value;
	
	if (type.value == w().TYPE.GPIO.value) {
		w().GPIO[value].mapped = true;
	}
}

WebIOPi.prototype.addALT = function (alt, gpio, name) {
	var o = Object();
	o.gpio = gpio;
	o.name = name;
	alt.gpios.push(o);
}

WebIOPi.prototype.updateValue = function (gpio, value) {
	w().GPIO[gpio].value = value;
	var style = (value == 1) ? "HIGH" : "LOW";
	$("#gpio"+gpio).attr("class", style);
}

WebIOPi.prototype.updateFunction = function (gpio, func) {
	w().GPIO[gpio].func = func;
	$("#function"+gpio).val(func);
	$("#function"+gpio).text(func);
}

WebIOPi.prototype.updateSlider = function (gpio, slider, value) {
	$("#"+slider+gpio).val(value);
}

WebIOPi.prototype.updateALT = function (alt, enable) {
	for (var p in alt.gpios) {
		gpio = alt.gpios[p].gpio;
		$("#description"+gpio).empty();
		if (enable) {
			$("#description"+gpio).append(alt.name + " " + alt.gpios[p].name);
			$("#gpio"+gpio).attr("class", alt.name);
			$("#function"+gpio).attr("class", "FunctionSpecial");
		}
		else {
			$("#description"+gpio).append("GPIO " + gpio);
			$("#gpio"+gpio).attr("class", "");
			$("#function"+gpio).attr("class", "FunctionBasic");
		}
	}
	alt.enabled = enable;
}

WebIOPi.prototype.updateUI = function () {
	$.getJSON(w().context + "*", function(data) {
		w().updateALT(w().ALT.I2C0, data["I2C0"]);
		w().updateALT(w().ALT.I2C1, data["I2C1"]);
		w().updateALT(w().ALT.SPI0, data["SPI0"]);
		w().updateALT(w().ALT.UART0, data["UART0"]);
		
		$.each(data["GPIO"], function(gpio, data) {
	    	w().updateFunction(gpio, data["function"]);
	    	if ((data["function"] == "IN") || (data["function"] == "OUT")) { 
	    		w().updateValue(gpio, data["value"]);
	    	}
	    	else if (data["function"] == "PWM") {
	    		w().updateSlider(gpio, "ratio", data["ratio"]);
	    		w().updateSlider(gpio, "angle", data["angle"]);
	    	}
	    	
		});
	});
	setTimeout(w().updateUI, 1000);
}


WebIOPi.prototype.checkVersion = function () {
	var version;
	
	$.get(w().context + "version", function(data) {
		_gaq.push(['_trackEvent', 'version', data]);
		version = data.split("/")[2];

		$.get("http://webiopi.trouch.com/version.php", function(data) {
			var lines = data.split("\n");
			var c = version.split(".");
			var n = lines[0].split(".");
			var updated = false;
			for (i=0; i<Math.min(c.length, n.length); i++) {
				if (n[i]>c[i]) {
					updated = true;
				}
			}
			if (updated || (n.length > c.length)) {
				var div = $('<div id="update"><a href="' + lines[1] + '">Update available</a></div>');
				$("body").append(div);
			}
		});
	});
}

WebIOPi.prototype.setValue = function (gpio, value, callback) {
	if (w().GPIO[gpio].func.toUpperCase()=="OUT") {
		$.post(w().context + 'GPIO/' + gpio + "/value/" + value, function(data) {
			w().updateValue(gpio, data);
			if (callback != undefined) {
				callback(gpio, data);
			}
		});
	}
	else {
		console.log(w().GPIO[gpio].func);
	}
}

WebIOPi.prototype.setFunction = function (gpio, func, callback) {
	$.post(w().context + 'GPIO/' + gpio + "/function/" + func, function(data) {
		w().updateFunction(gpio, data);
		if (callback != undefined) {
			callback(gpio, data);
		}
	});
}

WebIOPi.prototype.toggleValue = function (gpio) {
	var value = (w().GPIO[gpio].value == 1) ? 0 : 1;
	w().setValue(gpio, value);
}

WebIOPi.prototype.toggleFunction = function (gpio) {
	var value = (w().GPIO[gpio].func == "IN") ? "OUT" : "IN";
	w().setFunction(gpio, value)
}

WebIOPi.prototype.outputSequence = function (gpio, period, sequence, callback) {
	$.post(w().context + 'GPIO/' + gpio + "/sequence/" + period + "," + sequence, function(data) {
		w().updateValue(gpio, data);
		if (callback != undefined) {
			callback(gpio, data);
		}
	});
}

WebIOPi.prototype.callMacro = function (macro, args, callback) {
	$.post(w().context + 'macros/' + macro + "/" + args, function(data) {
		if (callback != undefined) {
			callback(macro, args, data);
		}
	});
}

WebIOPi.prototype.enablePWM = function(gpio, callback) {
	$.post(w().context + 'GPIO/' + gpio + "/pwm/enable", function(data) {
		if (callback != undefined) {
			callback(gpio, data);
		}
	});
}

WebIOPi.prototype.disablePWM = function(gpio, callback) {
	$.post(w().context + 'GPIO/' + gpio + "/pwm/disable", function(data) {
		if (callback != undefined) {
			callback(gpio, data);
		}
	});
}

WebIOPi.prototype.pulse = function(gpio, callback) {
	$.post(w().context + 'GPIO/' + gpio + "/pulse/", function(data) {
		if (callback != undefined) {
			callback(gpio, data);
		}
	});
}

WebIOPi.prototype.pulseRatio = function(gpio, ratio, callback) {
	$.post(w().context + 'GPIO/' + gpio + "/pulseRatio/" + ratio, function(data) {
		if (callback != undefined) {
			callback(gpio, data);
		}
	});
}

WebIOPi.prototype.pulseAngle = function(gpio, angle, callback) {
	$.post(w().context + 'GPIO/' + gpio + "/pulseAngle/" + angle, function(data) {
		if (callback != undefined) {
			callback(gpio, data);
		}
	});
}

WebIOPi.prototype.setLabel = function (id, label) {
	$("#" + id).val(label);
	$("#" + id).text(label);
}

WebIOPi.prototype.createButton = function (id, label, callback, callbackUp) {
	var button = $('<button type="button" class="Default">');
	button.attr("id", id);
	button.text(label);
	if ((callback != undefined) && (callbackUp == undefined)) {
		button.bind("click", callback);
	}
	else if ((callback != undefined) && (callbackUp != undefined)) {
		button.bind("mousedown", callback);
		button.bind("mouseup", callbackUp);
	}
	return button;
}

WebIOPi.prototype.createGPIOButton = function (gpio, label) {
	var button = w().createButton("gpio" + gpio, label);
	button.bind("click", function(event) {
		w().toggleValue(gpio);
	});
	return button;
}

WebIOPi.prototype.createFunctionButton = function (gpio) {
	var button = w().createButton("function" + gpio, " ");
	button.attr("class", "FunctionBasic");
	button.bind("click", function(event) {
		w().toggleFunction(gpio);
	});
	return button;
}

WebIOPi.prototype.createPulseButton = function (id, label, gpio) {
    var button = webiopi().createButton(id, label);
    button.bind("click", function(event) {
        webiopi().pulse(gpio);
    });
    return button;
}

WebIOPi.prototype.createMacroButton = function (id, label, macro, args) {
    var button = webiopi().createButton(id, label);
    button.bind("click", function(event) {
        webiopi().callMacro(macro, args);
    });
    return button;
}

WebIOPi.prototype.createSequenceButton = function (id, label, gpio, period, sequence) {
    var button = webiopi().createButton(id, label);
    button.bind("click", function(event) {
        webiopi().outputSequence(gpio, period, sequence);
    });
    return button;
}

WebIOPi.prototype.createRatioSlider = function(gpio) {
	var slider = $('<input type="range" min="0.0" max="1.0" step="0.01">');
	slider.attr("id", "ratio"+gpio);
	slider.bind("change", function() {
		w().pulseRatio(gpio, slider.val());
	});
	return slider;
}

WebIOPi.prototype.createAngleSlider = function(gpio) {
	var slider = $('<input type="range" min="-45" max="45" step="1">');
	slider.attr("id", "angle"+gpio);
	slider.bind("change", function() {
		w().pulseAngle(gpio, slider.val());
	});
	return slider;
}

WebIOPi.prototype.RPiHeader = function () {
	if (w()._header == undefined) {
		w()._header = new RPiHeader();
	}
	return w()._header;
}

function RPiHeader() {

}

RPiHeader.prototype.getPinCell = function (pin) {
	var cell = $('<td align="center">');
	var button;
	if (w().PINS[pin].type.value == w().TYPE.GPIO.value) {
		button = w().createGPIOButton(w().PINS[pin].value, pin);
	}
	else {
		var button = $('<button type="button">');
		button.val(pin);
		button.text(pin);
		button.attr("class", w().PINS[pin].type.style);
	}
	cell.append(button);
	return cell;
}

RPiHeader.prototype.getDescriptionCell = function (pin, align) {
	var cell = $('<td>');
	cell.attr("align", align);
	
	var div = $('<div>');
	div.attr("class", "Description");
	if (w().PINS[pin].type.value != w().TYPE.GPIO.value) {
		div.append(w().PINS[pin].value);
	}
	else {
		div.attr("id", "description"+w().PINS[pin].value);
		div.append("GPIO " + w().PINS[pin].value);
	}
	
	cell.append(div);

	return cell;
}

RPiHeader.prototype.getFunctionCell = function (pin) {
	var cell = $('<td align="center">');
	if (w().PINS[pin].type.value == w().TYPE.GPIO.value) {
		var button = w().createFunctionButton(w().PINS[pin].value);
		cell.append(button);
	}
	return cell;
}

RPiHeader.prototype.createTable = function (containerId) {
	var table = $("<table>");
	table.attr("id", "RPiHeader")
	for (var pin=1; pin<=26; pin++) {
		var line = 	$('<tr>');
		line.append(this.getFunctionCell(pin))
		line.append(this.getDescriptionCell(pin, "right"))
		line.append(this.getPinCell(pin));

		pin++;
		line.append(this.getPinCell(pin));
		line.append(this.getDescriptionCell(pin, "left"))
		line.append(this.getFunctionCell(pin))

		table.append(line);
	}
	
	if (containerId != undefined) {
		$("#"+containerId).append(table);
	}
	
	return table;
}

WebIOPi.prototype.Expert = function () {
	if (w()._expert == undefined) {
		w()._expert = new Expert();
	}
	return w()._expert;
}

function Expert() {
	
}

Expert.prototype.createGPIO = function (gpio) {
	var box = $("<div>");
	box.append(w().createFunctionButton(gpio));
	box.append(w().createGPIOButton(gpio, gpio));

	div = $('<div>');
	div.attr("id", "description"+gpio);
	div.attr("class", "Description");
	div.append("GPIO " + gpio);
	box.append(div);

	return box;
}

Expert.prototype.createList = function (containerId) {
	var box = $('<div>');
	
	for (i = 0; i<w().GPIO.length; i++) {
		if (w().GPIO[i].mapped == true) {
			var gpio = w().Expert().createGPIO(i);
			box.append(gpio);
		}
	}
		
	if (containerId != undefined) {
		$("#"+containerId).append(box);
	}
	
	return box;
} 


