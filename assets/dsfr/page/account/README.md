# account

Modèles de pages de connexion et création de compte

## Dépendances
```shell
account
└─ core
└─ connect
└─ form
└─ stepper
└─ alert
└─ radio
└─ input
└─ button
└─ checkbox
└─ password
```

## Utilisation
Afin d’utiliser le composant `account`, il est nécessaire d’ajouter les fichiers de styles et de scripts présents dans le dossier dist dans l'ordre suivant :\n
```html
<html>
  <head>
    <link href="css/core/core.min.css" rel="stylesheet">
    <link href="css/button/button.min.css" rel="stylesheet">
    <link href="css/connect/connect.min.css" rel="stylesheet">
    <link href="css/form/form.min.css" rel="stylesheet">
    <link href="css/link/link.min.css" rel="stylesheet">
    <link href="css/stepper/stepper.min.css" rel="stylesheet">
    <link href="css/alert/alert.min.css" rel="stylesheet">
    <link href="css/checkbox/checkbox.min.css" rel="stylesheet">
    <link href="css/radio/radio.min.css" rel="stylesheet">
    <link href="css/input/input.min.css" rel="stylesheet">
    <link href="css/password/password.min.css" rel="stylesheet">
  </head>
  <body>
    <script type="text/javascript" nomodule href="js/legacy/legacy.nomodule.min.js" ></script>
    <script type="module" href="js/core/core.module.min.js" ></script>
    <script type="text/javascript" nomodule href="js/core/core.nomodule.min.js" ></script>
    <script type="module" href="js/password/password.module.min.js" ></script>
    <script type="text/javascript" nomodule href="js/password/password.nomodule.min.js" ></script>
  </body>
</html>
```