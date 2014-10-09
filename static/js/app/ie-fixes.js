'use strict';

/* Console in older versions of IE is not supported */
if(!window.console) {
	console = {
			log: function() {},
			debug: function() {},
			info: function() {},
			warn: function() {},
			error: function() {}
	}
}
