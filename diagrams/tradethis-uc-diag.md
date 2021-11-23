---
puppeteer:
    landscape: true
    format: "letter"
    timeout: 3000 # <= wait 3 seconds before rendering in browser
---
# UML: Use Case Diagram

Generate use case diagram via plant url for mockup-trading website.

## Overview

Web app untuk melihat interaksi aset over time tanpa memikirkan resiko tambahan dengan data realtime yang akan terupdate setiap waktu

```plantuml
@startuml
left to right direction
skinparam packageStyle rectangle
skinparam actorstyle awesome
actor user
actor Old_user
actor New_user
rectangle Webapp {
  user <|- Old_user
  user <|- New_user
  user --> (Authenticate)
  (Authenticate) -- (Make transaction)
  (Make transaction) .> (Buy new asset) : extends
  (Make transaction) .>(Sell assets) : extends
  (Quote) <. (Make transaction) : extends
  (Make transaction)
  (Check log) <. (Make transaction) : extends
  (Make transaction) .> (Display asset) : include
}
@enduml
```
