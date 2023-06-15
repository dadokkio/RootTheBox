# BADGE GRAPHQL

- [BADGE GRAPHQL](#badge-graphql)
  - [Generate model](#generate-model)
  - [Execute](#execute)
  - [Sample query](#sample-query)

## Generate model
`sqlacodegen sqlite:///rootthebox.db > ../graph/app/models_original.py`

A subset of functionality has been kept in models.py

## Execute 
- [GUI LINK](http://localhost:7007/graphql)

## Sample query

```
# User data filtered by User note
me(where: {note: "xxx"}) {
  Handle
  Name
  team {
    Name
  }
}
```
```
# Team and teammate info filtered by User note
myteam(where: {note: "xxxx"}) {
  Name
  Motto
  user {
    edges {
      node {
        Name
      }
    }
  }
  money
}
```
```
# Scoreboard - first 10
teams(limit: 10, orderBy: "money", offset: 0) {
  timestamp
  records {
    Name
    money
  }
}
```