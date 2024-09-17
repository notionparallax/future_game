document.addEventListener("DOMContentLoaded", function(event) { 

  console.log("I'm here, I have a purpose!");
  console.log("velocity", $.Velocity);
  function randomArrows(){
    // console.log("mess up arrows");
    jQuery.each($("svg#network-2 #nodes g"), function(key, value){
      $(this).css("transform","rotateZ("+(Math.random()*365)+"deg)")
    });
  }

  function straightArrows(){
    // console.log("straighten arrows");
    jQuery.each($("svg#network-2 #nodes g"), function(key, value){
      //$(this).velocity({"rotateZ":"1deg"}); //can't get this to actually animate :(
      $(this).css("transform","rotateZ(1deg)")
    });
  }

  var hierarchySequence = [
    { e: $("#hierarchy-1 #grunts-observer"), p: { opacity:0.5                     }, o: {  duration: 100, loop: 3 } },
    { e: $("#hierarchy-1 #l-a-1"),           p: { strokeWidth: 10, strokeBlue:255 }, o: {  duration: 300          } },
    { e: $("#hierarchy-1 #use8203"),         p: { opacity:0.5                     }, o: {  duration: 70,  loop: 3 } },
    { e: $("#hierarchy-1 #l-b"),             p: { strokeWidth: 10, strokeBlue:255 }, o: {  duration: 300          } },
    { e: $("#hierarchy-1 #use8237"),         p: { opacity:0.5                     }, o: {  duration: 70,  loop: 3 } },
    { e: $("#hierarchy-1 #l-c"),             p: { strokeWidth: 10, strokeBlue:255 }, o: {  duration: 300          } },
    { e: $("#hierarchy-1 #the-boss"),        p: { opacity:0.5                     }, o: {  duration: 100, loop: 3 } },
    { e: $("#hierarchy-1 #r-c"),             p: { strokeWidth: 10, strokeBlue:255 }, o: {  duration: 300          } },
    { e: $("#hierarchy-1 #use8219"),         p: { opacity:0.5                     }, o: {  duration: 100, loop: 3 } },
    { e: $("#hierarchy-1 #r-b"),             p: { strokeWidth: 10, strokeBlue:255 }, o: {  duration: 300          } },
    { e: $("#hierarchy-1 #use8343"),         p: { opacity:0.5                     }, o: {  duration: 100, loop: 3 } },
    { e: $("#hierarchy-1 #r-a-2"),           p: { strokeWidth: 10, strokeBlue:255 }, o: {  duration: 300          } },
    { e: $("#hierarchy-1 #grunts-actor"),    p: { opacity:0.5                     }, o: {  duration: 100, loop: 3 } }
  ];

  var networkSequence1 = [
    { e: $("#network-1 #person09"),  p: { opacity:0.5                     }, o: {  duration: 100, loop: 3 } },
    { e: $("#network-1 #path104-1"), p: { strokeWidth: 10, strokeBlue:255 }, o: {  duration: 300          } },
    { e: $("#network-1 #person13"),  p: { opacity:0.5                     }, o: {  duration: 70,  loop: 3 } },
    { e: $("#network-1 #path144"),   p: { strokeWidth: 10, strokeBlue:255 }, o: {  duration: 300          } },
    { e: $("#network-1 #person05"),  p: { opacity:0.5                     }, o: {  duration: 70,  loop: 3 } },
    { e: $("#network-1 #path172"),   p: { strokeWidth: 10, strokeBlue:255 }, o: {  duration: 300          } },
    { e: $("#network-1 #person07"),  p: { opacity:0.5                     }, o: {  duration: 70,  loop: 3 } },

    { e: $("#network-1 #person16"),  p: { opacity:0.5                      }, o: {  duration: 100, loop: 3 } },
    { e: $("#network-1 #path164"),   p: { strokeWidth: 10, strokeGreen:255 }, o: {  duration: 300          } },
    { e: $("#network-1 #person15"),  p: { opacity:0.5                      }, o: {  duration: 70,  loop: 3 } },
    { e: $("#network-1 #path188"),   p: { strokeWidth: 10, strokeGreen:255 }, o: {  duration: 300          } },
    { e: $("#network-1 #person11"),  p: { opacity:0.5                      }, o: {  duration: 70,  loop: 3 } },
    { e: $("#network-1 #path120"),   p: { strokeWidth: 10, strokeGreen:255 }, o: {  duration: 300          } },
    { e: $("#network-1 #person05"),  p: { opacity:0.5                      }, o: {  duration: 70,  loop: 3 } },
    { e: $("#network-1 #path212"),   p: { strokeWidth: 10, strokeGreen:255 }, o: {  duration: 300          } },
    { e: $("#network-1 #person04"),  p: { opacity:0.5                      }, o: {  duration: 70,  loop: 3 } }
  ];

  $("#hierarchy-trigger").click(function(){
    console.log("you pressed the hierarchySequence button");
    $.Velocity.RunSequence(hierarchySequence);
  });
  $("#network-trigger1" ).click(function(){
    console.log("you pressed the networkSequence1 button");
    $.Velocity.RunSequence(networkSequence1);
  });

  var arrowState = "random";
  $("#network-trigger2").html("Infuse me with purpose");
  randomArrows();

  $("#network-trigger2" ).click(function(){
     console.log(arrowState);
     if (arrowState == "random"){
      straightArrows();
      arrowState = "straight";
      $("#network-trigger2").html("Let chaos rule!");
     }else{
      randomArrows();
      arrowState = "random";
      $("#network-trigger2").html("Infuse me with purpose");
     }

  });

});