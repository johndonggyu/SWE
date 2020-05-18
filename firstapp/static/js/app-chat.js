



(function (window, document, $) {

  $.app = $.app || {};

  var $body = $("body");
  var $window = $(window);

  $.app.menu = {
    is_touch_device: function () {
      var prefixes = ' -webkit- -moz- -o- -ms- '.split(' ');
      var mq = function (query) {
        return window.matchMedia(query).matches;
      }
      if (('ontouchstart' in window) || window.DocumentTouch && document instanceof DocumentTouch) {
        return true;
      }
      var query = ['(', prefixes.join('touch-enabled),('), 'heartz', ')'].join('');
      return mq(query);
    },

  };
 
})(window, document, jQuery);


var 
  chatOverlay = $(".chat-overlay"),
  chatContainer = $(".chat-container"),
  chatArea = $(".chat-area"),
  chatMessageSend = $(".chat-message-send");

$(document).ready(function () {
  if (!$.app.menu.is_touch_device()) {
    if (chatContainer.length > 0) {
      var chat_user_user = new PerfectScrollbar(".chat-container");
    }
  }
  else {
    $(".chat-container").css("overflow", "scroll");
  }

    $(this).addClass("active");
    chatArea.removeClass("d-none");


    chatContainer.animate({
      scrollTop: chatContainer[0].scrollHeight
    }, 400)
 

  $(window).on("resize", function () {
    if ($(window).width() > 992) {
      if (chatOverlay.hasClass("show")) {
        chatOverlay.removeClass("show");
      }
    }

  });
});
