function locoTrigger(){
    gsap.registerPlugin(ScrollTrigger);

    const locoScroll = new LocomotiveScroll({
    el: document.querySelector("#smooth-content"),
    smooth: true
    });
    locoScroll.on("scroll", ScrollTrigger.update);

    ScrollTrigger.scrollerProxy("#smooth-content", {
    scrollTop(value) {
        return arguments.length ? locoScroll.scrollTo(value, 0, 0) : locoScroll.scroll.instance.scroll.y;
    }, 
    getBoundingClientRect() {
        return {top: 0, left: 0, width: window.innerWidth, height: window.innerHeight};
    },
    pinType: document.querySelector("#smooth-content").style.transform ? "transform" : "fixed"
    });
    ScrollTrigger.addEventListener("refresh", () => locoScroll.update());

    ScrollTrigger.refresh();
}

locoTrigger()

// -------------------------------------------------------------------------------------

var crsr = document.querySelector(".cursor")
var main = document.querySelector(".main")
main.addEventListener("mousemove", function(dets){
    crsr.style.left = dets.x+"px"
    crsr.style.top = dets.y+"px"
})

// const mobile_icon = document.querySelector(".rght-nav2")
// const mobile_nav = document.querySelector("nav")

// mobile_icon.addEventListener("click", ()=>{
//     // alert("clicked")
//     mobile_nav.classList.toggle("nav-active")
// })


// -------------------------------------------------------------------------------------

function heroAnim(){
    var tl = gsap.timeline()

    tl.from(".hero-txt h1",{
        y:100,
        opacity:0,
        duration:0.5,
        delay:0.1,
        stagger:0.4
    },"hero-h1")
    tl.from(".neurons",{
        scale:0,
        opacity:0,
        duration:0.5,
        delay:0.4,
        stagger:0.3
    }, 'hero-imgs')
    tl.from("#rakshailogo",{
        scale:0,
        opacity:0,
        duration:0.5,
        stagger:0.3
    }, 'hero-imgs')
}

heroAnim()

function heroAnim2(){
    var tl1 = gsap.timeline({
        scrollTrigger:{
            trigger:".hero-txt h1",
            scroller:"#smooth-content",
            start:"top 23%",
            end:"top 0%",
            // markers:true,
            scrub:3
        }
    })
    tl1.to("#hero-txt-1",{
        x:-100,
        duration:1,
    }, "heroanim")
    tl1.to("#hero-txt-2",{
        x:100,
        duration:1,
    }, "heroanim")
    tl1.to("#rakshailogo",{
        y:-300,
        duration:1
    }, "heroanim")
}

heroAnim2()

var tl2 = gsap.timeline({
    scrollTrigger:{
        trigger:".hero-txt h1",
        scroller:".main",
        start:"top -35%",
        end:"top 100%",
        // markers:true,
        scrub:3
    }
})
tl2.from("#two-h2-head",{
    y:300,
    opacity:0,
    duration:0.5,
    delay:0.1,
    stagger:0.4
})
tl2.from("#two-h3-one",{
    y:100,
    opacity:0,
    duration:0.5,
    delay:0.1,
    stagger:0.4
})
tl2.from("#two-h3-two",{
    y:100,
    opacity:0,
    duration:0.5,
    delay:0.1,
    stagger:0.4
})
tl2.to(".main",{
    backgroundColor:"#fff"
}, 'a')
tl2.to(".cntr-nav",{
    opacity:0
}, 'a')
tl2.to(".neurons",{
    opacity:0,
}, "a")



var tl3 = gsap.timeline({
    scrollTrigger:{
        trigger:".hero-txt h1",
        scroller:".main",
        start:"top -125%",
        end:"top 260%",
        // markers:true,
        scrub:3
    }
})
tl3.to(".cntr-nav",{
    opacity:0
}, 'b')
tl3.to(".main",{
    backgroundColor:"#0F0D0D"
}, 'b')


const threeWrap = document.querySelector(".three-wrapper");
console.log(threeWrap.offsetWidth)

function threeScrollAmount(){
    let threeWrapWidth = threeWrap.scrollWidth;
    return -(threeWrapWidth - window.innerWidth)
}

var tl4 = gsap.timeline({
    scrollTrigger:{
        trigger:".three",
        scroller:".main",
        start:"top 0%",
        end:() => `+=${threeScrollAmount() * -1}`,
        // markers:true,
        pin: true,
        scrub:4,
        invalidateOnRefresh: true
    }
})
tl4.to(threeWrap,{
    x: threeScrollAmount,
    duration: 3,
    ease: "none"
})

// -------------------------------------------------------------------------------------------

