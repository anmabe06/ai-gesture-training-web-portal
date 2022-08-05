var tutorial = (function(){
    const possibleStatus = ["collect", "train", "play"];
    const driver = new Driver({
        allowClose: false,
        keyboardControl: true,
        onNext: (Element) => {
            if(!driver.hasNextStep()){
                setCookie("HasSeenTutorial", true);
            }
        }
        // doneBtnText: 'Terminado!', closeBtnText: 'Cerrar', nextBtnText: 'Siguiente', prevBtnText: 'Anterior',
    });

    async function loadTutorial(steps, stepNumber){
        listenToTutorialClose();
        driver.defineSteps(steps);
        driver.start(stepNumber);
    }

    async function getTutorialSteps(filePath, language){
        json = await $.getJSON(filePath);
        return json[language];
    }

    function getStepFilePath(status){
        return "./static/js/driver_steps/" + status + ".json";
    }

    function resetCookie(cname){
        document.cookie = cname +'=; Path=/; Expires=Thu, 01 Jan 1970 00:00:01 GMT;';
    }

    function getCookie(cname) {
        let name = cname + "=";
        let ca = decodeURIComponent(document.cookie).split(';');
        for(let i = 0; i <ca.length; i++) {
            let c = ca[i];
            while (c.charAt(0) == ' ') {
                c = c.substring(1);
            }
            if (c.indexOf(name) == 0) {
                return c.substring(name.length, c.length);
            }
        }
        return "";
    }

    function setCookie(cname, cvalue) {
        const d = new Date();
        //d.setTime(d.getTime() + (exdays*24*60*60*1000));
        //let expires = "expires="+ d.toUTCString();
        expires = "expires=" + d.getTime() + (20 * 365 * 24 * 60 * 60);
        console.log(cname + "=" + cvalue + ";" + expires);
        document.cookie = cname + "=" + cvalue + "; " + expires + '; Path=/;';
    }

    function listenToTutorialClose(){
        setTimeout(function(){
            document.getElementsByClassName("driver-close-btn")[0].addEventListener("click", function() {
                setCookie("HasSeenTutorial", true);
            });
        },100);
    }

    async function init(status, language="spanish", stepNumber=0, forceTutorialPlay=false){
        if(!(possibleStatus.includes(status))){
            throw "Page status is not contemplated on 'possibleStatus' array";
        }
        steps = await getTutorialSteps(getStepFilePath(status), language);

        if(forceTutorialPlay) resetCookie("HasSeenTutorial");

        try{
            if(!JSON.parse(getCookie("HasSeenTutorial"))) loadTutorial(steps, stepNumber);
        } catch (error){
            loadTutorial(steps, stepNumber);
        }

    }

    return {
        init,
    }
})();