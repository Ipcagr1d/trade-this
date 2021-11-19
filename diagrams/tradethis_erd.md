---
puppeteer:
    landscape: true
    format: "letter"
    timeout: 3000 # <= wait 3 seconds before rendering in browser
---

# Lemma

ERD for tradethis webapp, a mockup trading site where users can safely practice trading without any risk, all data entered must no be your actual data.

### Concept Diagram ERM

```plantuml
@startuml
digraph summary{
    enti1 [label="Users", shape=box, style=filled, fillcolor=aqua]
    enti2 [label="User", shape=box, style=filled, fillcolor=aqua]
    enti3[label="User_stock", shape=box, color=aqua]

    proc1 [label="Contains", shape=diamond]
    proc2 [label="Has", shape=diamond]

    attr1 [label="id"]
    attr2 [label="username"]
    attr3 [label="hash"]
    attr4 [label="wallet"]

    attr5 [label="user_id"]
    attr6 [label="symbol"]
    attr7 [label="shares"]
    attr8 [label="price"]
    attr9 [label="operation"]
    attr10 [label="time"]

    enti1 -> proc2 [label="n"]
    proc2 -> enti2 [label="1"]
    enti2 -> proc1 [label="1"]
    proc1 -> enti3 [label="1"]

    attr1 -> enti1
    attr2 -> enti1
    attr3 -> enti1
    attr4 -> enti1

    attr5 -> enti3
    attr6 -> enti3
    attr7 -> enti3
    attr8 -> enti3
    attr9 -> enti3
    attr10 -> enti3
}

@enduml
```

### ERD

```plantuml
@startuml
' hide the spot
hide circle

' avoid problems with angled crows feet
skinparam linetype ortho

entity "users" as users{
  *id : number <<generated>>
  --
  *username : text
  *hash : text <<generated>>
  *wallet : number
}

entity "users_stocks" as stock {
  *user_id : number <<generated>>
  --
  *symbol : text
  *shares : number
  *price : number
  *operation : text
  *date : date
}

users ||..o{ stock
@enduml
```
