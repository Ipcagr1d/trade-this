---
puppeteer:
    landscape: true
    format: "letter"
    timeout: 3000 # <= wait 3 seconds before rendering in browser
---
# UML: Activity Diagram

Generate Activity diagram via plant url for mockup-trading website.

## Overview

Web app untuk melihat interaksi aset over time tanpa memikirkan resiko tambahan dengan data realtime yang akan terupdate setiap waktu

```plantuml
@startuml
title Mockup Stock Trade Webapp

(*) --> "Handle Request"
--> "New session"
-> "Login page"
if "Authentication" then
    -->[success] "Get user data"
    if "Blank" then
        -->[true] "Generate default data"
    else
        ->[else] "Read user data"
    endif
else
    ->[failed] "Register page"
    if "User register" then
        ->[yes] "Generate default data"
    else
        ->[no] "Login page"
    endif
endif
"Read user data" --> ==PREP==
"Generate default data" --> ==PREP==
==PREP== --> "Parse user data"
==PREP== --> "Call API & Parse data"
"Call API & Parse data" --> "Populate index table"
"Parse user data" --> "Populate index table"
"Parse user data" --> "Generate history log"
"Populate index table" --> ==DISPLAY==
"Generate history log" --> ==DISPLAY==
==DISPLAY== --> "Display index page"
if "User action" then
    -->[buy] "Display buy page"
    if "Bought" then
        -->[yes] "Call API & parse data"
    else
        -->[no] "Display index page"
    endif
else
    -->[sell] "Display sell page"
    if "sold" then
        --> [yes] "Call API & parse data"
    else
        -->[no] "Display index page"
    endif
endif 
"Display index page" -> "Quit"
"Quit" -> "End Session"
"End Session" -> (*) 
"Display index page" -left-> "Parse"
"Parse" -> "Call API & parse data"
"Call API & parse data" --> "Update user data"
"Update user data" --> "Display index page" 

@enduml
```
