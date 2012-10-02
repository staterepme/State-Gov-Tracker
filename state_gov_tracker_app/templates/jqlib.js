/* This file is subject to the terms and conditions defined in
 * file 'LICENSE', which is part of this source code package.
 *       Copyright (c) 2010 SKR Farms (P) LTD.
 */

// When option is selected, use the value as url to change window.location
function gotoonselect( selector ) {
  $(selector).change( function(e) {
    url = $(selector).attr('value');
    window.location = url;
    e.stopPropagation();
  });
}

// Move (name,value) pairs from property object to DOM
function obj2node( props, node ) {
  for( k in props ) { 
    var n = typeof k === 'string' ? $('[name="'+k+'"]', node) : null;
    n ? n.html( props[k] ) : null;
  }
}

// Move (name,value) pairs from DOM to ``obj``. Use keys to select names
function node2obj( node, keys, obj ) {
  $.each(
    keys,
    function(i){ var k = keys[i]; obj[k] = $('[name="'+k+'"]', node).html(); }
  );
}

// Move (name,value) pairs from DOM to jQuery's link-data object.
function node2lnk( node, keys, lnkdata ) {
  $.each(
    keys,
    function(i){ 
      var k = keys[i], v = $('[name="'+k+'"]', node).html();
      $(lnkdata).setField( k, v );
    }
  );
}

// Use ``styles`` property to style the ``node``
function dostyles( node, styles ) {
  $.each(styles, function(k,v) { $(node).css(k,v) });
}

/*---- Plugin : Inline edit commiter 
 *  After an element get a focus and gets it content changed, the contents are
 *  submitted when focus leaves the element.
 */
(function($) {
  var onBlur = function(e) {
    var origValue = $(this).data( 'origValue' );
    var value = $(this).html();
    var params = {};
    var url = $(this).attr( 'data-url' );
    url = url ? url : e.data.url;
    if( value != origValue ) {
        for( var k in e.data.postdata ) {
          var v = $(this).attr( 'data-'+k )
          params[k] = v ? v : e.data.postdata[k]
        };
        params.value = params.value ? params.value : value;
        jqxhr = $.ajax({
          url : url,
          type : 'POST',
          data : params,
          beforeSend : function( jqXHR, sett ) {
            e.data.beforeSend( e.target, jqXHR, sett );
          },
          success : function( data, textStatus, jqXHR ) {
            e.data.success( e.target, data, textStatus, jqXHR );
          },
          error : function( jqXHR, textStatus, errorThrown ) {
            e.data.error( e.target, jqXHR, textStatus, errorThrown );
          }
        });
    }
    e.stopPropagation();
  };
  var onFocus = function(e) {
    $(this).data( 'origValue', $(this).html() );
  };

  $.fn.inlineEdit = function( opt ) {
    $(this).focus( onFocus )
    $(this).blur( opt, onBlur )
  }
})( jQuery );


/*---- Plugin : Helpboard for keyboard shortcuts 
 * Use push_keymap and pop_keymap to cascade keyboard interface.
 */

(function($) {
  var helplines = [];
  var code2text = {
      8: "backspace", 9: "tab",      13: "enter",    16: "shift",    17: "ctrl",
     18: "alt",      19: "pause",    20: "capslock", 27: "esc",      32: "space",
     33: "pageup",   34: "pagedown", 35: "end",      36: "home",     37: "left",
     38: "up",       39: "right",    40: "down",     45: "insert",   46: "del", 
     96: "0",        97: "1",        98: "2",        99: "3",        100: "4",
    101: "5",       102: "6",       103: "7",       104: "8",        105: "9",
    106: "*",       107: "+",       109: "-",       110: ".",        111: "/", 
    112: "f1",      113: "f2",      114: "f3",      115: "f4",       116: "f5",
    117: "f6",      118: "f7",      119: "f8",      120: "f9",       121: "f10",
    122: "f11",     123: "f12",     144: "numlock", 145: "scroll",   191: "/",
    224: "meta"
  };
  var _positionboard = function(nHelp) {
    var h = $(document).height(), w = $(document).width();
    var h_ = $(nHelp).height(), w_ = $(nHelp).width()
    h_ = h_ > h*0.8 ? h*0.8 : h_;   // Compute helpboard's height
    var styles = { 'max-height' : Math.ceil(h*0.8), 'left' : Math.ceil((w-w_)/2),
                   'top'        : Math.ceil( ((h-h_)/2) * 0.8 ) }
    return styles
  }
  var _showboard = function() {
    var nHelp = $('#helpboard');
    dostyles( nHelp, _positionboard(nHelp) ); // Style help board
    $(nHelp).fadeToggle(100);                // Toggle display
  };
  var _rendercolumn = function( helplines, from, size ) {
    lines = helplines.slice(from, size)
    $('#tmpl-helpcol').tmpl([lines]).appendTo( 'tr.helpboard' );
  }
  var onHelp = function(e) {
    var h = $(document).height();
    e.stopImmediatePropagation();
    e.preventDefault();
    if(! helplines.length ) { return; }  // No shortcuts defined
    var cols = Math.floor( helplines.length / Math.floor(h*0.8/30) ) + 1;
    cols = cols > 2 ? 2 : cols;          // Max. 2 columns allowed.
    var _maxrows = Math.floor(helplines.length / cols);
    $('tr.helpboard').empty();  // Empty helpboard, and refill with help text.
    for( i=0; i<helplines.length; i += _maxrows ) {
      if((i+_maxrows) >= helplines.length) { break; }
      _rendercolumn( helplines, i, _maxrows );
    }
    _rendercolumn( helplines, i, helplines.length )
    _showboard();
  }
  var keymap_handler = function(e) {
    var key = String([e.altKey, e.ctrlKey, e.shiftKey, e.keyCode]);
    var kmap = $(e.data.jqobj).data( 'kmap' );
    var hndlr = kmap ? kmap[key] : null;
    // Same handler is used to invoke subscribed handlers and to show the
    // help-board.
    if( $('#helpboard').css('display') != 'none' ) {
      e.stopImmediatePropagation();
      e.preventDefault();
      $('#helpboard').fadeOut(100);
    } else if( e.shiftKey && e.keyCode == 191) {  // if '?' then show helpboard
      onHelp(e)
    } else if(hndlr && hndlr.length==3) {
      hndlr[0](e, hndlr[1]);
    };
  };
  var makehelplines = function(kmap) {
    var makehelpline = function(k, help) {
      var key = ''; 
      k = k.split(',');
      if(k.length != 4) { return ''; }
      key += k[0] == 'true' ? 'Alt+' : '';
      key += k[1] == 'true' ? 'Ctrl+' : '';
      key += k[2] == 'true' ? 'Shift+' : '';
      key += ( code2text[k[3]] ? code2text[k[3]] 
                : String.fromCharCode(k[3]).toLowerCase() ) + ' : ';
      x = { 'key' : key, 'text' : help }
      return x;
    }
    $.each( kmap,
      function(k,v){ 
        if(k && kmap[k]) {
          x = makehelpline(k, kmap[k][2]);
          if(x) { helplines[helplines.length]=x }
        }
      }
    );
    return helplines;
  }

  $.fn.push_keymap = function( keymaps ) {      // Plugin API
    var currkm = this.data('kmap');
    var Newkm = function(){};
    if(currkm) {
      Newkm.prototype = currkm;
      Newkm.prototype.constructor = Newkm;
    } else {
      Newkm.prototype.constructor = Newkm;
    }
    // Keymaps is a map of 
    // { 'altKey,ctrlKey,shiftKey,keyCode' : <handler> }
    var kmap = new Newkm();
    kmap.up = currkm ? currkm : null;
    $.extend( kmap, keymaps );
    this.data('kmap', kmap);
    if(! currkm ) {
      this.bind( 'keydown.keymap', {'jqobj': this}, keymap_handler );
    }
    // Compute helplines;
    helplines = [];
    helplines = makehelplines(kmap);
    return this;
  };

  $.fn.pop_keymap = function() {                // Plugin API
    var kmap = this.data('kmap');
    kmap ? this.data('kmap', kmap.up) : null;
    kmap && (kmap.up == null) ? this.unbind( 'keydown.keymap' ) : null;
    helplines = [];
    helplines = kmap && kmap.up ? makehelplines(kmap.up) : [];
    return this;
  };

})( jQuery );



/*---- Plugin : seeAndEdit
 * Involves three nodes, nTrigger, nView and nForm. Use nTrigger to toggle
 * between nView node and nForm node. When nView is displayed nForm will be
 * hidden and vice versa.
 */

(function($) {
  var onFormShow = function(opt) {
    var nForm = opt.nForm, nView = opt.nView;
    var lnkdata = {};
    if( nForm ) {
      // Pull the form from previous parent and corresponding view.
      $(nForm).data('nView') ?  $($(nForm).data('nView')).show() : null;
      $(nForm).remove();

      $(nForm).link(lnkdata); // Gather form's initial values.

      // Remebber the form's current parent and corresponding view.
      $(nForm).data('nView', nView);

      // Insert form, filling it with the corresponding view's data.
      $($(nView)[0].parentNode).append(nForm);
      node2lnk( opt.nView, opt.keys, lnkdata );

      // Subscribe submit-handler.
      $(nForm).bind( 'submit', opt, opt.onFormSubmit );

      // Animate
      $(nView).slideUp(opt.speed, function() { 
        $(nForm).slideDown(opt.speed, function() {
          opt.cbFormShow ? opt.cbFormShow(opt) : null;  // Callback
        })
      });
    }
  };

  var onFormHide = function(opt) {
	if( opt.nForm ) {
	  $(opt.nForm).unbind( 'submit', opt.onFormSubmit );
	  $(opt.nForm).slideUp(opt.speed, function() {
        $(opt.nView).show();
        opt.cbFormHide ? opt.cbFormHide(opt) : null;    // Callback
      });
    }
  };

  var onFormSuccess = function(opt, data, textStatus, xhr) {
    obj2node(data, opt.nView);
    opt.onFormHide(opt);
    opt.cbFormSubmit ? opt.cbFormSubmit(opt) : null;    // Callback
  }
  var onFormError = function(opt, xhr, textStatus, error) {
    err = 'Error : ' + error;
    opt.cbFormSubmit ? opt.cbFormSubmit(opt) : null;    // Callback
    opt.nFlash ? $(opt.nFlash).css('color', 'red').html(err).fadeOut(2000) : null;
  }
  var onFormSubmit = function(e) {
    var opt = e.data;
    var nForm = opt.nForm, nView = opt.nView, nFlash = opt.nFlash;
    var postUrl = opt.getPostUrl ? opt.getPostUrl(opt) : $(nView).attr('posturl');
    if( postUrl ) {
	  jqxhr = $.ajax(
	    postUrl,
	    { type : opt.ajaxMethod,
	      data : $(this).serialize(),
	      success : function( data, textStatus, xhr ) {
            opt.onFormSuccess(opt, data, textStatus, xhr)
          },
	      error : function( xhr, textStatus, error ) {
            opt.onFormError(opt, xhr, textStatus, error)
          }
	    }
	  );
    }
	e.preventDefault();
	e.stopImmediatePropagation();
  }

  var onTrigger = function(e) {
    var nView = e.data.nView, nTrigger = e.data.nTrigger;
    var opt = e.data;
    opt.cbTrigger ? opt.cbTrigger(opt) : null;
    $(nView).css('display') != "none" ? opt.onFormShow(opt) : opt.onFormHide(opt);
  }

  $.fn.seeAndEdit = function(opt) {                     // Plugin API
    // nTrigger node must note be inside nView or nForm
    // nView and nForm must be independent and should not nest under each other.
    var _opt = {
      nTrigger      : null,             // Mandatory
      nView         : null,             // Mandatory
      nForm         : null,             // Mandatory
      onTrigger     : onTrigger,
      onFormShow    : onFormShow,
      onFormHide    : onFormHide,
      onFormSubmit  : onFormSubmit,
      onFormSuccess : onFormSuccess,
      onFormError   : onFormError,
      cbFormShow    : null,
      cbFormHide    : null,
      cbFormSubmit  : null,
      cbTrigger     : null,
      getPostUrl    : null,
      speed         : 0,
      nFlash        : $('.flash', opt.nForm),
      ajaxMethod    : 'POST'
    }
    $.extend( _opt, opt )
    $(_opt.nTrigger).click( _opt, _opt.onTrigger )
    return this;
  }
})( jQuery );


/*---- Plugin : navUpDown */
(function($) {
  var onKeyJ = function(e, opt) {
    var idx = null;
    var nodes = $(opt.nodes);
    if(opt.curridx == null) {
      idx = 0;
    } else if ( (opt.curridx+1) < nodes.length) {
      idx = opt.curridx+1;
      $(nodes[opt.curridx]).css( 'border', opt.normalCSS );
    } else {
      idx = nodes.length;
    }
    $(nodes[idx]).css('border', opt.highlightCSS);
    opt.curridx = idx;
  }
  var onKeyK = function(e, opt) {
    var idx = null;
    var nodes = $(opt.nodes);
    if(opt.curridx == null) {
      idx = 0;
    } else if ( opt.curridx > 0) {
      idx = opt.curridx-1;
      $(nodes[opt.curridx]).css( 'border', opt.normalCSS )
    } else {
      idx = 0
    }
    $(nodes[idx]).css('border', opt.highlightCSS);
    opt.curridx = idx;
  }
  var onKeyO = function(e, opt) {
    console.log('Opening ...');
  }
  $.fn.navUpDown = function(opt) {           //--- Plugin API
    var _opt = {
      nodes : null,
      curridx : null,
      highlightCSS : '2px solid gray',
      keymaps : {}
    }
    opt ? $.extend( _opt, opt ) : null;
    $.extend(opt, _opt)
	var keymaps = {
      'false,false,false,74' : [ onKeyJ, opt, 'Move to next entry' ],
      'false,false,false,75' : [ onKeyK, opt, 'Move to previus entry' ],
      'false,false,false,79' : [ onKeyO, opt, 'Open current entry' ]
	};
    $.extend( keymaps, opt.keymaps );
    $(document).push_keymap( keymaps );
    return this;
  }
})( jQuery );


/*--- Third party code ---*/

/*
 * CSS Browser Selector v0.4.0 (Nov 02, 2010)
 * Rafael Lima (http://rafael.adm.br)
 * http://rafael.adm.br/css_browser_selector
 * License: http://creativecommons.org/licenses/by/2.5/
 * Contributors: http://rafael.adm.br/css_browser_selector#contributors
 * */
function css_browser_selector(u){var ua=u.toLowerCase(),is=function(t){return ua.indexOf(t)>-1},g='gecko',w='webkit',s='safari',o='opera',m='mobile',h=document.documentElement,b=[(!(/opera|webtv/i.test(ua))&&/msie\s(\d)/.test(ua))?('ie ie'+RegExp.$1):is('firefox/2')?g+' ff2':is('firefox/3.5')?g+' ff3 ff3_5':is('firefox/3.6')?g+' ff3 ff3_6':is('firefox/3')?g+' ff3':is('gecko/')?g:is('opera')?o+(/version\/(\d+)/.test(ua)?' '+o+RegExp.$1:(/opera(\s|\/)(\d+)/.test(ua)?' '+o+RegExp.$2:'')):is('konqueror')?'konqueror':is('blackberry')?m+' blackberry':is('android')?m+' android':is('chrome')?w+' chrome':is('iron')?w+' iron':is('applewebkit/')?w+' '+s+(/version\/(\d+)/.test(ua)?' '+s+RegExp.$1:''):is('mozilla/')?g:'',is('j2me')?m+' j2me':is('iphone')?m+' iphone':is('ipod')?m+' ipod':is('ipad')?m+' ipad':is('mac')?'mac':is('darwin')?'mac':is('webtv')?'webtv':is('win')?'win'+(is('windows nt 6.0')?' vista':''):is('freebsd')?'freebsd':(is('x11')||is('linux'))?'linux':'','js']; c = b.join(' '); h.className += ' '+c; return c;}; css_browser_selector(navigator.userAgent);
