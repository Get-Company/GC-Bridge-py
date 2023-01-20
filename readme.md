# Readme for Python

## ENV
Install ENV by:

    pip3 install virtualenv

### Create the new environment:

    python -m venv *name_of_the_environment*

### Delete the environment: Simply delete the folder

    rmdir *name_of_the_environment*

### Activate it:

    .\*name_of_the_environment*\Scripts\activate
    .\project_env\Scripts\activate

### Deactivate it:

    deactivate


<hr>

## ERP COM Object

### Installation
Unbedingt die virtuelle Umgebung aktivieren. Dann:

    pip3 install pywin32

Oder in der Requirements.txt nachschauen bzw. die installieren

## Compile Script to exe
https://datatofish.com/executable-pyinstaller/

<hr>

## Date



## Forms and DB

### Forms
https://www.youtube.com/watch?v=uZnp21fu8TQ

### DB
https://www.youtube.com/watch?v=70mNRClYJko

    pip install flask-sqlalchemy

Set standard values for fields, if they aren't set

    def__init__(self, name, email):
        self.name = name
        self.email = email

If the database isn't created yet, paste these Python Console:

    from src.app import db
    from src.Entity.Bridge.BridgeCategoryEntity import BridgeCategoryEntity
    from src.Entity.Bridge.BridgeSynchronizeEntity import BridgeSynchronizeEntity
    db.create_all()

#### Update
Get the object like

    anschrift_flo = BridgeAnschriftenEntity.query.filter_by(id=1).first()

Now access and change its fields like
    
    anschrift_flo.na2 = "Fliriin Bichnir"

Add it to the session and commit the change to the db

    db.session.add(anschrift_flo)
    db.session.commit()

If you access another table through relationship. You have to add and commit the Parent!!!
Example: Get Anschriften by Adressen

    adressen_flo = BridgeAdressenEntity.query.filter_by(id=1).first()
    anschrift_flo = adressen_flo.anschriften

Now you can change the fields of anschrift

    anschrift_flo[0].na2 = "Flörian Böchner"

Now add the anschrift back to the parent Adressen

    adressen_flo.anschriften = anschrift_flo

Ok, now you have to add and commit adressen for changing the anschriften

    db.session.add(adressen_flo)
    db.session.commit()

Everything is fine!

#### Query example:
    box = BridgeProductEntity.query.filter_by(erp_nr="104014").first()
    print("Product(%s) %s | Mappei(%s) %s | Price: CL %s / MA %s" % (
        box.erp_nr,
        box.name,
        box.mappei[0].nr,
        box.mappei[0].name,
        box.price,
        box.mappei[0].prices[0].price_high)
          )


#### Migration
Nicht app.run starten!
Die FLASK_APP env variable muss auf das Hauptprogramm gesetzt werden, da hier alles zusammenläuft. PyCharm oder WindowsPowershell

    $env:FLASK_APP = "main/gcbridge.py"
    set FLASK_APP=main/gcbridge.py

https://flask.palletsprojects.com/en/2.0.x/cli/

Jetzt kann mit der WindowsShell eine Veränderung festgestellt:

    flask db migrate -m "Commit Text"

Und die Veränderung durchgeführt werden:

    flask db upgrade


<hr>

#### DB set current state as right
Set the stamp head

    flask db stamp head

Make migration

    flask db migrate

Upgrade to set the current db as right

    flask db upgrade


## Pip3

### List all Packages

    pip3 list

### Make requirements.txt with all packages from the environment

    pip3 freeze --local > requirements.txt

### Uninstall all

    pip3 uninstall -r requirements.txt -y

Combine them by &&

    pip3 freeze > requirements.txt && pip3 uninstall -r requirements.txt -y

<hr>

## Script

### Run forever

    while True:
        # some python code that I want 
        # to keep on running
        # it stops, when it gets False

# Errors

### Has no attribute
### SetTypelibForAllClsids(mod.CLSIDToClassMap) AttributeError: module 'win32com.gen_py.C74FB8F0-A6EF-11D2-B95E-004005232B30x0x1x0' has no attribute 'CLSIDToClassMap'
Geh zum Verzeichnis:

    C:\Users\fbuchner.CLASSEI\AppData\Local\Temp\gen_py\3.10

Lösche den Ordner aus der Fehlermeldung (C74FB8F0-A6EF-11D2-B95E-004005232B30x0x1x0)

# Translation

## LibreTranslate
https://github.com/LibreTranslate/LibreTranslate

### Docker Image

    docker run -it -p 5000:5000 libretranslate

localhost:5000

### Python Package

    pip3 install libretranslatepy
    
    from libretranslatepy import LibreTranslateAPI
    lt = LibreTranslateAPI("http://localhost:5000/")
    print(lt.detect("Hallo Welt"))
    print(lt.languages())
    print(lt.translate("Hallo Übersetzer", "de", "en"))


<hr>


# Abfragen
## Preiserhöhung - Preise Mappei nach Land
    
    SELECT
        mappei.nr, 
        mappei_price.price_quantity, 
        IFNULL(price_low,price_high)price_low 
    FROM 
        mappei_product_entity as mappei, 
        mappei_price_entity as mappei_price
    WHERE 
        mappei_price.land = "de"
    AND 
        mappei_price.product_id = mappei.id


# Docker Compose examples
## A more extensicve and separated example
    
    version: '3'

    services:
    shop:
    container_name: dw__myshop_shopware
    image: dockware/flex:latest
    ports:
    - "22:22"     # ssh
      - "80:80"     # apache2
      - "8888:8888" # watch admin
      - "9998:9998" # watch storefront proxy (not needed if you start with "make watch-storefront")
      - "9999:9999" # watch storefront
      volumes:
      - "dw__shopware_myshop_volume:/var/www/html"
      networks:
      - web
      links:
      - mailcatcher:mailserver # as we want to get your mails in mailcatcher we have to link it here
      environment:
      - XDEBUG_ENABLED=1    # as a frontend dev I would set to 0 for performance
      - FILEBEAT_ENABLED=0
    
    # -----------------------------------------------------------------------
    mailcatcher:
    container_name: dw__myshop_mailcatcher
    image: schickling/mailcatcher
    ports:
    - "1080:1080" # simple call it with http://localhost:1080, for sure you can choose any port you wan't on the left side of the mapping.
    networks:
      - web
    # -----------------------------------------------------------------------
    
    db:
    container_name: dw__myshop_db
    image: mysql:5.7 # if you want a different mysql Version just choose one: https://hub.docker.com/_/mysql?tab=tags
    command: mysqld --sql_mode="ERROR_FOR_DIVISION_BY_ZERO,NO_AUTO_CREATE_USER,NO_ENGINE_SUBSTITUTION" --thread_stack=400000
    volumes:
    - "dw__db_myshop_volume:/var/lib/mysql"
    ports:
      - "3306:3306"
      networks:
      - web
      environment:
      - MYSQL_ROOT_PASSWORD=root
      - MYSQL_PASSWORD=root
      - MYSQL_DATABASE=myshop_db
      - TZ=Europe/Berlin
    # -----------------------------------------------------------------------
    
    redis:
    container_name: dw__myshop_redis
    image: redis:4.0
    ports:
    - "6379:6379"
    networks:
      - web
      volumes:
      - dw__redis__myshop_volume:/data
    # -----------------------------------------------------------------------
    adminer: # to open it :http://localhost:8080, server: db, user:root, pwd:root
    image: adminer
    container_name: dw__myshop_adminer
    restart: always
    ports:
    - 8080:8080
    networks:
      - web
    
    
    ## ***********************************************************************
    ##  PERSISTENT DOCKER VOLUMES
    ## ***********************************************************************
    volumes:
    dw__db_myshop_volume:
    driver: local
    dw__shopware_myshop_volume:
    driver: local
    dw__redis__myshop_volume:
    driver: local
    
    ## ***********************************************************************
    ##  NETWORKS
    ## ***********************************************************************
    networks:
    web:
    external: false