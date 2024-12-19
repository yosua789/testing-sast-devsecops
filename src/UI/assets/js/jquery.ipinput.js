/*!
 * jQuery Input Ip : v0.1 (2016/03/22 03:27:00)
 * Copyright (c) 2016 Juan Pablo Tosso
 * Licensed under the MIT license and GPL licenses.
 *
 */
(function ( $ ) {
  var methods = {
      init : function(options) {
          this.addClass( "ipinput");
          for(var i =0; i < 4;i++)
          {
            var inp = $('<input size="3" type="text" maxlength="3">');
            var div = this;
            this.append(inp);
            if(i<3)
            {
              this.append('.');
            }
            inp.keyup(function () {
              if (this.value.length == this.maxLength) {
                if(parseInt(this.value)>255)
                {
                  var t = $(this);
                  t.closest('div').addClass('highlighted');
                  setTimeout(function(){
                    t.closest('div').removeClass('highlighted');
                  }, 2000);
                  this.value="";
                }else
                  $(this).next('input').focus();
              }
              var ip = "";
              for(var i = 0; i < 4; i++)
              {
                ip += div.children('input').eq(i).val();
                if(i<3)
                  ip +=('.');
              }
              div.children('input').eq(4).val(ip);
            });
          }
          this.append($('<input type="hidden" name="' + this.data('name') + '" value="">'));
          this.ipinput('setaddress', this.data('ip'));
          return this;
      },
      setaddress : function(ip) {
        var s = ip.split('.');
        for(var i = 0; i < 4; i++)
        {
          this.children('input').eq(i).val(s[i]);
        }
        this.children('input').eq(4).val(ip);
      }
  };

    $.fn.ipinput = function(options) {
      if ( methods[options] ) {
          return methods[ options ].apply( this, Array.prototype.slice.call( arguments, 1 ));
      } else if ( typeof options === 'object' || ! options ) {
          // Default to "init"
          return methods.init.apply( this, arguments );
      } else {
          $.error( 'Method ' +  options + ' does not exist on jQuery.ipinput' );
      }
    };
}( jQuery ));
