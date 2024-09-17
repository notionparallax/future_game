document.addEventListener('DOMContentLoaded', function() {
  //er, if I need events...
  //ga('send', 'event', 'scrolled', 'x', 'y');
  //ga('send', 'event', [eventCategory], [eventAction], [eventLabel], [eventValue], [fieldsObject]);

  function registerPocketSave() {
    console.log("looking for pockets");
    // chrome only so far
    var target = document.querySelector('body');

    // create an observer instance
    var observer = new MutationObserver(function(mutations) {
      mutations.forEach(function(mutation) {
        //console.log(mutation);
        let a = document.getElementById('pkt_ext_master');
        if (a) {
          console.log(a, "found a pocket save - firing a GA event!");
          ga('send', 'event', 'Pocketed', document.title);
          observer.disconnect(); //once we've saved to pocket, stop so that we don't get ghost versions
        }
      });
    });

    // configuration of the observer:
    var config = { attributes: true, childList: true, characterData: true };

    // pass in the target node, as well as the observer options
    observer.observe(target, config);
  }
  registerPocketSave();
});
